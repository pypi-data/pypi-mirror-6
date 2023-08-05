#
# DecoTengu - dive decompression library.
#
# Copyright (C) 2013 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
DecoTengu dive decompression engine.

[mpdfd] Powell, Mark. Deco for Divers, United Kingdom, 2010
"""

from functools import partial
from collections import namedtuple, OrderedDict
import math
import logging

from .model import ZH_L16B_GF
from .error import ConfigError
from .ft import recurse_while, bisect_find
from .flow import coroutine
from .const import METER_TO_BAR

EPSILON = 10 ** -10

logger = logging.getLogger('decotengu.engine')

class Phase(object):
    """
    Dive phase enumeration.

    The dive phases are

    START
        Start of a dive. It happens at begining of the dive (time=0min,
        depth=0min). Only one dive step can exist with such dive phase.
    DESCENT
        Descent during dive - current dive step is deeper than previous one.
    CONST
        Constant depth during dive - current dive step is at the same depth as
        previous one.
    ASCENT
        Ascent during dive - current dive step is shallower than previous one.
    DECOSTOP
        Decompression stop. Current dive step is at the same depth as previous
        one and ascent is not possible until allowed by decompression model.
    """
    START = 'start'
    DESCENT = 'descent'
    CONST = 'const'
    ASCENT = 'ascent'
    DECOSTOP = 'decostop'


Step = namedtuple('Step', 'phase depth time pressure gas data prev')
Step.__repr__ = lambda s: 'Step(phase="{}", depth={}, time={},' \
    ' pressure={:.4f}, gf={:.4f})'.format(
        s.phase, s.depth, s.time, s.pressure, s.data.gf
    )
Step.__doc__ = """
Dive step information.

:var phase: Dive phase.
:var depth: Depth of dive [m].
:var time: Time of dive [s].
:var pressure: Pressure at depth [bar].
:var gas: Gas mix configuration.
:var data: Decompression model data.
:var prev: Previous dive step.
"""

GasMix = namedtuple('GasMix', 'depth o2 n2 he')
GasMix.__doc__ = """
Gas mix configuration.

:var depth: Gas mix switch depth.
:var o2: O2 percentage.
:var n2: N2 percentage.
:var he: Helium percentage.
"""

DecoStop = namedtuple('DecoStop', 'depth time')
DecoStop.__doc__ = """
Dive decompression stop information.

:var depth: Depth of decompression stop [m].
:var time: Length of decompression stops [min].
"""


class Engine(object):
    """
    DecoTengu decompression engine.

    Use decompression engine to calculate dive profile and decompression
    information.

    :var model: Decompression model.
    :var surface_pressure: Surface pressure [bar].
    :var ascent_rate: Ascent rate during a dive [m/min].
    :var descent_rate: Descent rate during a dive [m/min].
    :var _gas_list: List of gas mixes.
    :var _deco_stop_search_time: Time limit for decompression stop linear
        search.
    """
    def __init__(self):
        super().__init__()
        self.model = ZH_L16B_GF()
        self.surface_pressure = 1.01325
        self.ascent_rate = 10.0
        self.descent_rate = 20.0

        self._gas_list = []
        self._deco_stop_search_time = 64


    def _to_pressure(self, depth):
        """
        Convert depth in meters to absolute pressure in bars.

        :param depth: Depth in meters.
        """
        return depth * METER_TO_BAR + self.surface_pressure


    def _to_depth(self, time, rate):
        """
        Convert time into depth using depth change rate.

        :param time: Time in seconds.
        :param rate: Rate of depth change [m/min].
        """
        return time * rate / 60


    def _to_time(self, depth, rate):
        """
        Convert depth into time using depth change rate.

        The time is returned in seconds.

        :param depth: Depth in meters.
        :param rate: Rate of depth change [m/min].
        """
        return depth / rate * 60


    def _inv_ascent(self, step):
        """
        Return true if ascent from a depth is possible.

        Step's pressure is compared to maximum allowed tissue pressure. The
        latter is calculated using configured gradient factor low value.

        :param step: Dive step containing pressure information.
        """
        return step.pressure > self.model.pressure_limit(step.data)


    def _inv_deco_stop(self, step, gas, gf):
        """
        Return true if one should stay at a decompression stop.

        Tissue pressure limit is calculated for next decompression stop
        (using gradient factor value) and it is checked that ascent to next
        stop is not possible.

        :param step: Dive step - current decompression stop.
        :param gas: Gas mix configuration.
        :param gf: Gradient factor value for next decompression stop.
        """
        ts_3m = self._to_time(3, self.ascent_rate)
        data = self._tissue_pressure_ascent(step.pressure, ts_3m, gas, step.data)
        max_tp = self.model.pressure_limit(data, gf=gf)
        return self._to_pressure(step.depth - 3) <= max_tp


    def _step(self, phase, prev, depth, time, gas, data):
        """
        Create dive step record.

        The dive step's pressure is calculated from the depth parameters.
        The configured GF low value is used if gradient factor not
        specified.

        :param phase: Dive phase (see Phase enum).
        :param prev: Previous dive step.
        :param depth: Depth of dive step.
        :param time: Time at which dive step is recorded (in seconds since start
                     of a dive).
        :param gas: Gas mix configuration.
        :param data: Decompression model data.
        """
        p = self._to_pressure(depth)
        return Step(phase, depth, time, p, gas, data, prev)


    def _step_next(self, step, time, gas, phase='const'):
        """
        Calculate next dive step at constant depth and advanced by
        specified amount of time.

        :param step: Current dive step.
        :param time: Time spent at current depth [s].
        :param gas: Gas mix configuration.
        :param data: Decompression model data.
        :param phase: Dive phase.
        """
        data = self._tissue_pressure_const(step.pressure, time, gas, step.data)
        return self._step(phase, step, step.depth, step.time + time, gas, data)


    def _step_next_descent(self, step, time, gas, phase='descent'):
        """
        Calculate next dive step when descent is performed for specified
        period of time.

        :param step: Current dive step.
        :param time: Time to descent [s].
        :param gas: Gas mix configuration.
        :param phase: Dive phase.
        """
        data = self._tissue_pressure_descent(step.pressure, time, gas, step.data)
        depth = step.depth + self._to_depth(time, self.descent_rate)
        return self._step(phase, step, depth, step.time + time, gas, data)


    def _step_next_ascent(self, step, time, gas, gf=None, phase='ascent'):
        """
        Calculate next dive step when ascent is performed for specified
        period of time.

        FIXME: due to ``gf`` parameter this method is deco model dependant,
               this has to be improved

        :param step: Current dive step.
        :param time: Time to ascent [s].
        :param gas: Gas mix configuration.
        :param data: Decompression model data.
        :param phase: Dive phase.
        """
        data = self._tissue_pressure_ascent(step.pressure, time, gas, step.data)
        depth = step.depth - self._to_depth(time, self.ascent_rate)
        step = self._step(phase, step, depth, step.time + time, gas, data)
        if gf is not None:
            # FIXME: make it model independent
            data = data._replace(gf=gf)
            step = step._replace(data=data)
        return step


    def _tissue_pressure_const(self, abs_p, time, gas, data):
        """
        Calculate tissues gas loading after exposure for specified time at
        constant pressure.

        :param abs_p: The pressure indicating the depth [bar].
        :param time: Time at pressure in seconds.
        :param gas: Gas mix configuration.
        :param data: Decompression model data.
        """
        return self.model.load(abs_p, time, gas, 0, data)


    def _tissue_pressure_descent(self, abs_p, time, gas, data):
        """
        Calculate tissues gas loading after descent from pressure for
        specified amount of time.

        :param abs_p: Starting pressure indicating the depth [bar].
        :param time: Time of descent in seconds.
        :param gas: Gas mix configuration.
        :param data: Decompression model data.
        """
        rate = self.descent_rate * METER_TO_BAR
        data = self.model.load(abs_p, time, gas, rate, data)
        return data


    def _tissue_pressure_ascent(self, abs_p, time, gas, tp_start):
        """
        Calculate tissues gas loading after ascent from pressure for
        specified amount of time.

        :param abs_p: Starting pressure indicating the depth [bar].
        :param time: Time of ascent in seconds.
        :param gas: Gas mix configuration.
        :param tp_start: Initial tissues pressure.
        """
        rate = -self.ascent_rate * METER_TO_BAR
        tp = self.model.load(abs_p, time, gas, rate, tp_start)
        return tp


    def _dive_descent(self, depth, gas):
        """
        Dive descent from surface to specified depth.

        :param depth: Destination depth.
        :param gas: Gas mix configuration.
        """
        data = self.model.init(self.surface_pressure)
        step = self._step('start', None, 0, 0, gas, data)
        yield step

        time = self._to_time(depth, self.descent_rate)
        logger.debug('descent for {}s'.format(time))
        step = self._step_next_descent(step, time, gas)
        yield step
        logger.debug('descent finished at {}m'.format(step.depth))


    def _dive_ascent(self, start):
        """
        Dive ascent from specified dive step.

        The ascent is divided into two phases

        - ascent to first decompression stop or surface
        - ascent performing decompression stops, if necessary

        :param start: Starting dive step.
        """
        step = start

        stages = self._free_ascent_stages()
        for step in self._free_staged_ascent(step, stages):
            yield step

        if step.depth == 0:
            return

        stages = self._deco_ascent_stages(step.depth)
        yield from self._deco_staged_ascent(step, stages)


    def _find_first_stop(self, start, depth, gas):
        """
        Find first decompression stop depth using Schreiner equation and
        bisect algorithm.

        The depth is searched between depth indicated by starting dive step
        and depth parameter (the latter can be 0 (surface) or any other
        depth (divisible by 3, depth stop candidate).

        The depth of first decompression stop is the shallowest depth,
        which does not breach the ascent limit imposed by maximum tissue
        pressure limit. The depth is divisble by 3.

        :param start: Starting dive step indicating current depth.
        :param depth: Depth limit - surface or gas switch depth.
        :param gas: Gas mix configuration.
        """
        assert start.depth > depth
        assert depth % 3 == 0

        ts_3m = self._to_time(3, self.ascent_rate)

        t = self._to_time(start.depth - depth, self.ascent_rate)
        dt = t % ts_3m

        # bisect search solution range: 0 <= k < n - 1; the invariant
        # function will use k + 1 as it does not make sense to ascent
        # by 0m
        n = t // ts_3m
        logger.debug(
            'find first stop: {}m -> {}m, {}s, n={}, dt={}s'
                .format(start.depth, depth, start.time, n, dt)
        )
        assert t >= 0
        assert 0 <= dt < ts_3m, dt
        #assert start.depth - n * 3 == depth

        # for each k ascent for (k + 1) * t(3m) + dt seconds and check if
        # ascent invariant is not violated; (k + 1) * t(3m) + dt formula
        # gives first stop candidates as multiples of 3m
        f = lambda k, step: self._inv_ascent(
            self._step_next_ascent(step, (k + 1) * ts_3m + dt, gas)
        )
        # find largest k for which ascent without decompression is possible
        k = bisect_find(n, f, start)
        k += 1  # the invariant function uses k + 1

        if k == n:
            depth = None
            logger.debug('find first stop: no deco zone found')
        elif k == 0:
            depth = start.depth
            logger.debug('already at deco zone')
        else:
            t = k * ts_3m + dt
            depth = start.depth - self._to_depth(t, self.ascent_rate)
            logger.debug(
                'find first stop: found, free from {} to {}, ascent time={}' \
                    .format(start.depth, depth, t)
            )

        assert not depth or round(depth, 10) % 3 == 0, \
            'Invalid first stop depth {}'.format(depth)

        return depth


    def _free_ascent_stages(self):
        """
        Calculate stages for deco-free ascent.

        Ascent stage is a tuple

        - destination depth
        - gas mix

        The ascent stages are calculated using gas mix list. The
        destination depth is gas switch depth rounded up to multiply of 3m,
        for example::

             0m  21%        24m  21%
            22m  50%   ->    6m  50%
             6m 100%         0m 100%

        """
        mixes = zip(self._gas_list[:-1], self._gas_list[1:])
        yield from ((((m2.depth - 1) // 3 + 1) * 3, m1) for m1, m2 in mixes)
        yield (0, self._gas_list[-1])


    def _deco_ascent_stages(self, start_depth):
        """
        Calculate stages for decompression ascent.

        Ascent stage is a tuple

        - destination depth
        - gas mix

        The ascent stages are calculated using gas mix list. The
        destination depth is gas switch depth rounded down to multiply of
        3m, for example::

             0m  21%        21m  21%
            22m  50%   ->    6m  50%
             6m 100%         0m 100%

        Only gas mixes, which switch depth is shallower than start depth,
        are used for decompression ascent stages calculation.

        :param start_depth: Decompression start depth.
        """
        assert start_depth != 0
        mixes = zip(self._gas_list[:-1], self._gas_list[1:])
        yield from (
            (m2.depth // 3 * 3, m1) for m1, m2 in mixes
            if m2.depth < start_depth
        )
        yield (0, self._gas_list[-1])


    def _switch_gas(self, step, gas):
        """
        Switch to specified gas mix, ascending if necessary.

        The method is used to switch gas during dive ascent when ascent is
        performed to depth being multiply of 3m. Two scenarios are
        implemented

        #. Gas mix switch depth is the same as current dive step depth,
           then simply perform gas mix switch.
        #. Gas mix switch depth is shallower than current dive step depth

           - ascend to gas mix switch depth
           - perform gas mix switch
           - ascend to next depth, which is multiply of 3m

        Gas mix switch is done in place, takes no time at the moment, but
        in the future this should be configurable.

        A tuple of gas mix switch dive steps is returned.

        :param step: Current dive step.
        :param gas: Gas to switch to.

        .. seealso:: :func:`decotengu.engine.Engine._can_switch_gas`
        """
        logger.debug('switching to gas {} from {}'.format(gas, step.depth))
        assert step.depth - gas.depth < 3
        if step.depth == gas.depth:
            steps = (step._replace(gas=gas),)
        else:
            assert step.depth > gas.depth
            s1 = self._free_ascent(step, gas.depth, gas)
            s2 = s1._replace(gas=gas)
            s3 = self._free_ascent(s2, gas.depth // 3 * 3, gas)
            steps = (s1, s2, s3)
        return steps


    def _can_switch_gas(self, start, gas):
        """
        Check if gas mix can be switched to without violating decompression
        model ascent invariant.

        If gas mix switch is possible, then gas mix switch dive steps are
        returned, null otherwise.

        :param step: Current dive step.
        :param gas: Gas to switch to.

        .. seealso:: :func:`decotengu.engine.Engine._switch_gas`
        """
        gs_steps = self._switch_gas(start, gas)
        return gs_steps if self._inv_ascent(gs_steps[-1]) else None


    def _free_staged_ascent(self, start, stages):
        """
        Perform staged ascent until first decompression stop.

        :param start: Starting dive step.
        :param stages: Dive stages.

        .. seealso:: :func:`decotengu.engine.Engine._ascent_stages_free`
        """
        step = start
        for depth, gas in stages:
            if step.depth - gas.depth < 3:
                # if gas switch drives us into deco zone, then stop ascent
                # leaving `step` as first decompression stop
                gs_steps = self._can_switch_gas(step, gas)
                if gs_steps:
                    step = gs_steps[-1]
                    yield from gs_steps
                else:
                    logger.debug('gas switch into deco zone, revert')
                    break

            # check if there is first decompression stop at this ascent
            # stage
            stop = self._find_first_stop(step, depth, gas)
            if stop and stop == step.depth:
                break
            elif stop:
                step = self._free_ascent(step, stop, gas)
                yield step
                break
            else:
                step = self._free_ascent(step, depth, gas)
                yield step


    def _deco_staged_ascent(self, start, stages):
        """
        Perform staged asccent within decompression zone.

        :param start: Starting dive step.
        :param stages: Dive stages.

        .. seealso:: :func:`decotengu.engine.Engine._ascent_stages_deco`
        """
        step = start
        assert round(step.depth, 10) % 3 == 0 and step.depth > 0, step.depth
        n_stops = step.depth / 3
        gf_step = (self.model.gf_high - self.model.gf_low) / n_stops
        logger.debug('deco engine: gf step={:.4}'.format(gf_step))
        first_stop = step.depth
        for depth, gas in stages:
            if step.depth >= gas.depth and gas.depth != 0:
                for step in self._switch_gas(step, gas):
                    yield step
            gf = self.model.gf_low + (first_stop - step.depth) / 3 * gf_step
            for step in self._deco_ascent(step, depth, gas, gf, gf_step):
                yield step
        logger.debug('deco engine: gf at surface={:.4f}'.format(step.data.gf))


    def _free_ascent(self, start, depth, gas):
        """
        Ascent to destination depth using gas mix.

        The ascent is performed without performing any decompression stops.
        It is caller resposibility to provide the destination depth outside
        of decompression zone.

        :param start: Dive step indicating current depth.
        :param depth: Destination depth.
        :param gas: Gas mix configuration.
        """
        dt = self._to_time(start.depth - depth, self.ascent_rate)
        time = start.time + dt
        return self._step_next_ascent(start, dt, gas)


    def _deco_ascent(self, first_stop, depth, gas, gf_start, gf_step):
        """
        Ascent from first decompression stop to the destination depth.

        The depth of first stop should be divisible by 3. The depth of last
        step is at value indicated by ``depth`` value (0 if at surface).
        There is no decompression at the destination depth performed.

        Tissue gas loading is performed using gas mix configuration.

        The length of a decompression stop is guarded by gradient factor
        start value and gradient factor step - the decompression stop lasts
        until it is allowed to ascent to next stop (see _inv_ascent
        method).

        :param first_stop: Dive stop indicating first decompression stop.
        :param depth: Destination depth.
        :param gas: Gas mix configuration.
        :param gf_start: Gradient factor start value for the first stop.
        :param gf_step: Gradient factor step to calculate gradient factor
                        value for next stops.
        """
        step = first_stop
        max_time = self._deco_stop_search_time * 60

        assert round(step.depth, 10) % 3 == 0 and step.depth > 0, step.depth
        assert abs(step.depth - depth) > EPSILON, '{} vs. {}' \
                .format(step.depth, depth)

        n_stops = round((step.depth - depth) / 3)
        logger.debug('stops={}, gf start={:.4}, gf step={:.4}' \
                .format(n_stops, gf_start, gf_step))

        for k_stop in range(n_stops):
            logger.debug('deco stop: k_stop={}, depth={}'.format(k_stop, step.depth))
            gf = gf_start + k_stop * gf_step

            inv_f = partial(self._inv_deco_stop, gas=gas, gf=gf + gf_step)
            l_step_next_f = partial(self._step_next, time=max_time, gas=gas)
            l_step = recurse_while(inv_f, l_step_next_f, step)
            logger.debug('deco stop: linear find finished at {}'.format(l_step))

            b_step_next_f = lambda k, step: True if k == 0 else \
                    inv_f(self._step_next(step, k * 60, gas, gf))
            k = bisect_find(max_time + 1, b_step_next_f, l_step)

            t = round(l_step.time - step.time + (k + 1) * 60)
            logger.debug('deco stop: search completed {}m, {}s, n2={.n2}%,' \
                ' gf={:.4}'.format(step.depth, t, gas, gf))
            assert t % 60 == 0, t

            step = self._step_next(step, t, gas, phase='decostop')
            yield step

            ts_3m = self._to_time(3, self.ascent_rate)
            step = self._step_next_ascent(step, ts_3m, gas, gf + gf_step)
            yield step


    def add_gas(self, depth, o2):
        """
        Add gas mix to the gas mix list.

        Rules

        #. First gas mix switch depth should be 0m.
        #. Second or later gas mix switch depth should be greater than 0m.
        #. Third or later gas mix switch depth should be shallower than the
           last one.

        :param depth: Switch depth of gas mix.
        :param o2: O2 percentage.
        """
        if len(self._gas_list) == 0 and depth != 0:
            raise ValueError('First gas mix switch depth should be at 0m')
        elif len(self._gas_list) > 0 and depth == 0:
            raise ValueError('Second or later gas mix switch depth should' \
                ' be > 0m')

        if len(self._gas_list) > 1 and self._gas_list[-1].depth < depth:
            raise ValueError('Gas mix switch depth should be shallower than' \
                ' last one')

        self._gas_list.append(GasMix(depth, o2, 100 - o2, 0))


    def calculate(self, depth, time):
        """
        Start dive calculations for specified dive depth and bottom time.

        The method returns an iterator of dive steps.

        :param depth: Maximum depth [m].
        :param time: Bottom time [min].
        """
        if len(self._gas_list) == 0:
            raise ConfigError('No gas mixes configured')

        gas = self._gas_list[0]

        for step in self._dive_descent(depth, gas):
            yield step

        step = self._step_next(step, time * 60, gas)
        yield step

        yield from self._dive_ascent(step)



class DecoTable(object):
    """
    Decompression table summary.

    The class is coroutine class - create coroutine object, then call it to
    start the coroutine.

    The decompression stops time is in minutes.

    .. seealso:: :class:`decotengu.engine.DecoStop`
    """
    def __init__(self):
        """
        Create decompression table summary.
        """
        self._stops = OrderedDict()


    @property
    def total(self):
        """
        Total decompression time.
        """
        return sum(s.time for s in self.stops)


    @property
    def stops(self):
        """
        List of decompression stops.
        """
        times = (math.ceil((s[1] - s[0]) / 60) for s in self._stops.values())
        stops = [DecoStop(d, t) for d, t in zip(self._stops, times) if t > 0]

        assert all(s.time > 0 for s in stops)
        assert all(s.depth > 0 for s in stops)

        return stops


    @coroutine
    def __call__(self):
        """
        Create decompression table coroutine to gather decompression stops
        information.
        """
        stops = self._stops = OrderedDict()
        while True:
            step = yield
            if step.phase == 'decostop':
                depth = step.depth
                if depth in stops:
                    stops[depth][1] = step.time
                else:
                    stops[depth] = [step.prev.time, step.time]


# vim: sw=4:et:ai
