#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Python class for Forza Motorsport 7's data stream format.

Copyright (c) 2018 Morten Wang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from struct import calcsize, unpack

## Documentation of the packet format is available on
## https://forums.forzamotorsport.net/turn10_postsm926839_Forza-Motorsport-7--Data-Out--feature-details.aspx#post_926839

class ForzaDataPacket:
    ## Class variables are the specification of the format and the names of all
    ## the properties found in the data packet.

    ## Format string that allows unpack to process the data bytestream
    ## for the V1 format called 'sled'
    sled_format = '<iI' + 'f' * 51 + 'i' * 5

    ## Format string for the V2 format called 'car dash'
    dash_format = sled_format + 'f' * 17 + 'H' + 'B' * 6 + 'b' * 3

    ## Packed byte sizes of each format, derived from the struct strings so
    ## the FH4 splice below stays correct if a format string ever changes.
    SLED_SIZE = calcsize(sled_format)
    DASH_SIZE = calcsize(dash_format)

    ## FH4 inserts this many unknown bytes right after the sled section.
    FH4_PADDING = 12

    ## Names of the properties in the order they're featured in the packet:
    sled_props = [
        'is_race_on', 'timestamp_ms',
        'engine_max_rpm', 'engine_idle_rpm', 'current_engine_rpm',
        'acceleration_x', 'acceleration_y', 'acceleration_z',
        'velocity_x', 'velocity_y', 'velocity_z',
        'angular_velocity_x', 'angular_velocity_y', 'angular_velocity_z',
        'yaw', 'pitch', 'roll',
        'norm_suspension_travel_FL', 'norm_suspension_travel_FR',
        'norm_suspension_travel_RL', 'norm_suspension_travel_RR',
        'tire_slip_ratio_FL', 'tire_slip_ratio_FR',
        'tire_slip_ratio_RL', 'tire_slip_ratio_RR',
        'wheel_rotation_speed_FL', 'wheel_rotation_speed_FR',
        'wheel_rotation_speed_RL', 'wheel_rotation_speed_RR',
        'wheel_on_rumble_strip_FL', 'wheel_on_rumble_strip_FR',
        'wheel_on_rumble_strip_RL', 'wheel_on_rumble_strip_RR',
        'wheel_in_puddle_FL', 'wheel_in_puddle_FR',
        'wheel_in_puddle_RL', 'wheel_in_puddle_RR',
        'surface_rumble_FL', 'surface_rumble_FR',
        'surface_rumble_RL', 'surface_rumble_RR',
        'tire_slip_angle_FL', 'tire_slip_angle_FR',
        'tire_slip_angle_RL', 'tire_slip_angle_RR',
        'tire_combined_slip_FL', 'tire_combined_slip_FR',
        'tire_combined_slip_RL', 'tire_combined_slip_RR',
        'suspension_travel_meters_FL', 'suspension_travel_meters_FR',
        'suspension_travel_meters_RL', 'suspension_travel_meters_RR',
        'car_ordinal', 'car_class', 'car_performance_index',
        'drivetrain_type', 'num_cylinders'
    ]

    ## The additional props added in the 'car dash' format
    dash_props = ['position_x', 'position_y', 'position_z',
                  'speed', 'power', 'torque',
                  'tire_temp_FL', 'tire_temp_FR',
                  'tire_temp_RL', 'tire_temp_RR',
                  'boost', 'fuel', 'dist_traveled',
                  'best_lap_time', 'last_lap_time',
                  'cur_lap_time', 'cur_race_time',
                  'lap_no', 'race_pos',
                  'accel', 'brake', 'clutch', 'handbrake',
                  'gear', 'steer',
                  'norm_driving_line', 'norm_ai_brake_diff']

    ## Single source of truth mapping each packet format to its (struct
    ## format string, ordered property names). Resolved once per packet
    ## rather than re-branched at every call site.
    FORMATS = {
        'sled': (sled_format, sled_props),
        'dash': (dash_format, sled_props + dash_props),
        'fh4':  (dash_format, sled_props + dash_props),
    }

    def __init__(self, data, packet_format='dash'):
        ## The format this data packet was created with:
        self.packet_format = packet_format

        struct_format, self.props = self.FORMATS[packet_format]

        if packet_format == 'fh4':
            ## FH4 inserts FH4_PADDING unknown bytes right after the sled
            ## section; strip them so the remaining bytes match the standard
            ## 'dash' layout.
            dash_start = self.SLED_SIZE + self.FH4_PADDING
            data = data[:self.SLED_SIZE] \
                + data[dash_start:dash_start + (self.DASH_SIZE - self.SLED_SIZE)]

        ## zip makes for convenient flexibility when mapping names to
        ## values in the data packet:
        for prop_name, prop_value in zip(self.props,
                                         unpack(struct_format, data)):
            setattr(self, prop_name, prop_value)

    @classmethod
    def get_props(cls, packet_format = 'dash'):
        '''
        Return the list of properties in the data packet, in order.

        :param packet_format: which packet format to get properties for,
                              one of 'sled', 'dash', or 'fh4'
        :type packet_format: str
        '''
        return cls.FORMATS[packet_format][1]

    def to_list(self, attributes=None):
        '''
        Return the values of this data packet, in order. If a list of
        attributes is provided, only return those; otherwise return every
        property in this packet's format.

        :param attributes: the attributes to return
        :type attributes: list
        '''
        return [getattr(self, a) for a in (attributes or self.props)]

    def get_tsv_header(self):
        '''
        Return a tab-separated string with the names of all properties in the
        order defined in the data packet.
        '''
        return '\t'.join(self.props)

    def to_tsv(self):
        '''
        Return a tab-separated values string with all data in the given order.
        All floating point numbers are formatted with fixed precision so the
        number of significant digits can be changed in one place if desired.
        '''
        return '\t'.join(format(v, 'f') if isinstance(v, float) else str(v)
                         for v in self.to_list())
