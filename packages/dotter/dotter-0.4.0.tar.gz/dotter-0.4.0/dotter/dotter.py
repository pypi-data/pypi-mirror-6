# -*- coding: utf-8 -*-
"""
dotter

Copyright (c) 2013-2014, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

"""
import os
from base64 import b16encode
from subprocess import PIPE, Popen


class Program:

    """
    These values can be used as valid render engine

    """
    Circo = 'circo'
    Dot = 'dot'
    Fdp = 'fdp'
    Neato = 'neato'
    Sfdp = 'sfdp'
    Twopi = 'twopi'


class RankType:

    """
    These values can be used for Dotter.rank()

    """
    Max = 'max'
    Min = 'min'
    Same = 'same'
    Sink = 'sink'
    Source = 'source'


class Shape:

    """
    These values can be used as valid shape values.
    See http://www.graphviz.org/doc/info/shapes.html for more information.

    """
    Assembly = 'assembly'
    Box = 'box'
    Box3d = 'box3d'
    Cds = 'cds'
    Circle = 'circle'
    Component = 'component'
    Diamond = 'diamond'
    Doublecircle = 'doublecircle'
    Doubleoctagon = 'doubleoctagon'
    Egg = 'egg'
    Ellipse = 'ellipse'
    Fivepoverhang = 'fivepoverhang'
    Folder = 'folder'
    Hexagon = 'hexagon'
    House = 'house'
    Insulator = 'insulator'
    Invhouse = 'invhouse'
    Invtrapezium = 'invtrapezium'
    Invtriangle = 'invtriangle'
    Larrow = 'larrow'
    Lpromoter = 'lpromoter'
    Mcircle = 'Mcircle'
    Mdiamond = 'Mdiamond'
    Msquare = 'Msquare'
    Note = 'note'
    Noverhang = 'noverhang'
    Octagon = 'octagon'
    Oval = 'oval'
    Parallelogram = 'parallelogram'
    Pentagon = 'pentagon'
    Plaintext = 'plaintext'
    Point = 'point'
    Polygon = 'polygon'
    Primersite = 'primersite'
    Promoter = 'promoter'
    Proteasesite = 'proteasesite'
    Proteinstab = 'proteinstab'
    Rarrow = 'rarrow'
    Rect = 'rect'
    Rectangle = 'rectangle'
    Restrictionsite = 'restrictionsite'
    Ribosite = 'ribosite'
    Rnastab = 'rnastab'
    Rpromoter = 'rpromoter'
    Septagon = 'septagon'
    Signature = 'signature'
    Square = 'square'
    Star = 'star'
    Tab = 'tab'
    Terminator = 'terminator'
    Threepoverhang = 'threepoverhang'
    Trapezium = 'trapezium'
    Triangle = 'triangle'
    Tripleoctagon = 'tripleoctagon'
    Underline = 'underline'
    Utr = 'utr'


class Style:

    """
    These values can be used as valid node style values.
    See http://www.graphviz.org/doc/info/shapes.html#d:style for more info.

    """
    Bold = 'bold'
    Dashed = 'dashed'
    Diagonals = 'diagonals'
    Dotted = 'dotted'
    Filled = 'filled'
    Invisible = 'invisible'
    Rounded = 'rounded'
    Solid = 'solid'


class Dotter:

    def __init__(self, directed=True, output_to_file=True,
                 output_filename=None, output_type=None, program=Program.Dot,
                 strict=False):
        self.directed = directed

        self.args = [program]

        if output_to_file:
            if output_filename:
                if output_type is None:
                    _unused, file_ext = os.path.splitext(output_filename)
                    output_type = file_ext[1:].lower()

                self.args.append('-o')
                self.args.append(output_filename)
            else:
                self.args.append('-O')

        if output_type is None:
            output_type = 'pdf'
        self.args.append('-T%s' % output_type)

        self.commands = []
        if strict:
            self.execute(' strict ')
        if self.directed:
            self.execute('digraph')
        else:
            self.execute('graph')
        self.execute(' {')

    def __str__(self):
        return '\n'.join(self.commands)

    def execute(self, command):
        self.commands.append(command)

    def close(self):
        self.execute('}')
        p = Popen(self.args, stdout=PIPE, stdin=PIPE)
        commands = '\n'.join(self.commands)
        commands = commands.encode(encoding='utf-8')
        out, _unused_err = p.communicate(commands)
        out = out.decode(encoding='utf-8')
        return out

    @staticmethod
    def escape(s):
        try:
            s = b16encode(bytes(s, encoding='utf-8')).decode(encoding='utf-8')
        except TypeError:
            s = b16encode(s)
        for i in range(10):
            s = s.replace(chr(ord('0') + i), chr(ord('a') + i))
        return s

    def add_edge(self, node1, node2, label=None):
        if self.directed:
            fmt = '{0} -> {1}'
        else:
            fmt = '{0} -- {1}'
        if label:
            fmt += ' [label="{0}"]'.format(label)
        self.execute(fmt.format(Dotter.escape(node1), Dotter.escape(node2)))

    def add_node(self, node, font=None, fontsize=None, label=None, shape=None,
                 url=None, styles=None):
        self.execute('{0}'.format(Dotter.escape(node)))
        self.set_label(node, label if label else node)
        self.node_attributes(node, font, fontsize, shape, url, styles)

    def node_attributes(self, node, font=None, fontsize=None, shape=None,
                        url=None, styles=None):
        if font:
            cmd = '{0} [fontname="{1}"]'.format(Dotter.escape(node), font)
            self.execute(cmd)
        if fontsize:
            cmd = '{0} [fontsize="{1}"]'.format(Dotter.escape(node), fontsize)
            self.execute(cmd)
        if shape:
            cmd = '{0} [shape="{1}"]'.format(Dotter.escape(node), shape)
            self.execute(cmd)
        if url:
            cmd = '{0} [URL="{1}"]'.format(Dotter.escape(node), url)
            self.execute(cmd)
        if styles:
            style = ', '.join(styles)
            cmd = '{0} [style="{1}"]'.format(Dotter.escape(node), style)
            self.execute(cmd)

    def set_label(self, node, label):
        self.execute('{0} [label="{1}"]'.format(Dotter.escape(node), label))

    def set_position(self, node, x, y):
        if not self.args[0] in [Program.Fdp, Program.Neato]:
            raise Warning()

        self.execute('{} [pos="{},{}!"]'.format(Dotter.escape(node), x, y))

    def nodes_attributes(self, font=None, shape=None):
        if font:
            self.execute('node [fontname="{}"]'.format(font))
        if shape:
            self.execute('node [shape="{}"]'.format(shape))

    def rank(self, nodes, rank_type=RankType.Same):
        nodes = ' '.join(Dotter.escape(node) for node in nodes)
        cmd = '{rank=%s; %s}' % (rank_type, nodes)
        self.execute(cmd)
