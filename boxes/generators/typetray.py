#!/usr/bin/env python3
# Copyright (C) 2013-2014 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *
from boxes.lids import _TopEdge

class TypeTray(_TopEdge):
    """Type tray - allows only continuous walls"""

    ui_group = "Tray"

    def __init__(self):
        Boxes.__init__(self)
        self.addTopEdgeSettings(fingerjoint={"surroundingspaces": 0.5},
                                roundedtriangle={"outset" : 1})
        self.buildArgParser("sx", "sy", "h", "hi", "outside", "bottom_edge",
                            "top_edge")
        self.argparser.add_argument(
            "--back_height",  action="store", type=float, default=0.0,
            help="additional height of the back wall - e top egde only")
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=0.0,
            help="radius for strengthening side walls with back_height")
        self.argparser.add_argument(
            "--gripheight", action="store", type=float, default=30,
            dest="gh", help="height of the grip hole in mm")
        self.argparser.add_argument(
            "--gripwidth", action="store", type=float, default=70,
            dest="gw", help="width of th grip hole in mm (zero for no hole)")

    def xSlots(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            posy = 0
            for y in self.sy:
                self.fingerHolesAt(posx, posy, y)
                posy += y + self.thickness

    def ySlots(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            posx = 0
            for x in reversed(self.sx):
                self.fingerHolesAt(posy, posx, x)
                posx += x + self.thickness

    def xHoles(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.hi)

    def yHoles(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.hi)

    def gripHole(self):
        if not self.gw:
            return

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        r = min(self.gw, self.gh) / 2.0
        self.rectangularHole(x / 2.0, self.gh * 1.5, self.gw, self.gh, r)

    def render(self):
        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.sy = self.adjustSize(self.sy)
            self.h = self.adjustSize(self.h, e2=False)
            if self.hi:
                self.hi = self.adjustSize(self.hi, e2=False)

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        y = sum(self.sy) + self.thickness * (len(self.sy) - 1)
        h = self.h
        sameh = not self.hi
        hi = self.hi = self.hi or h
        t = self.thickness


        # outer walls
        b = self.bottom_edge
        t1, t2, t3, t4 = self.topEdges(self.top_edge)
        self.closedtop = self.top_edge in "fFh"

        bh = self.back_height if self.top_edge == "e" else 0.0

        # x sides

        self.ctx.save()

        # outer walls
        self.rectangularWall(x, h+bh, [b, "F", t1, "F"],
                             callback=[self.xHoles, None, self.gripHole],
                             ignore_widths=[] if bh else [1, 6],
                             move="up")
        if bh:
            self.rectangularWall(x, h, [b, "f", t3, "f"],
                                 callback=[self.mirrorX(self.xHoles, x), ],
                                 move="up")
        else:
            self.rectangularWall(x, h, [b, "F", t3, "F"],
                                 callback=[self.mirrorX(self.xHoles, x), ],
                                 ignore_widths=[1, 6], move="up")

        # floor
        if b != "e":
            self.rectangularWall(x, y, "ffff", callback=[
                self.xSlots, self.ySlots], move="up")

        # Inner walls

        be = "f" if b != "e" else "e"

        for i in range(len(self.sy) - 1):
            e = [edges.SlottedEdge(self, self.sx, be), "f",
                 edges.SlottedEdge(self, self.sx[::-1], "e", slots=0.5 * hi), "f"]
            if self.closedtop and sameh:
                e = [edges.SlottedEdge(self, self.sx, be), "f",
                     edges.SlottedEdge(self, self.sx[::-1], "f", slots=0.5 * hi), "f"]

            self.rectangularWall(x, hi, e, move="up")

        # top / lid
        if self.closedtop and sameh:
            e = "FFFF" if self.top_edge == "f" else "ffff"
            self.rectangularWall(x, y, e, callback=[
                self.xSlots, self.ySlots], move="up")
        else:
            self.drawLid(x, y, self.top_edge)

        self.ctx.restore()
        self.rectangularWall(x, hi, "ffff", move="right only")

        # y walls

        # outer walls

        if bh:
            self.trapezoidSideWall(
                y, h, h+bh, [b, "f", "e", "h"],
                radius=self.radius, callback=[self.yHoles, ], move="up")
            self.trapezoidSideWall(
                y, h+bh, h, [b, "h", "e", "f"], radius=self.radius,
                callback=[self.mirrorX(self.yHoles, y), ], move="up")
        else:
            self.rectangularWall(
                y, h, [b, "f", t2, "f"], callback=[self.yHoles, ],
                ignore_widths=[1, 6], move="up")
            self.rectangularWall(
                y, h, [b, "f", t4, "f"],
                callback=[self.mirrorX(self.yHoles, y), ],
                ignore_widths=[1, 6], move="up")

        # inner walls
        for i in range(len(self.sx) - 1):
            e = [edges.SlottedEdge(self, self.sy, be, slots=0.5 * hi),
                 "f", "e", "f"]
            if self.closedtop and sameh:
                e = [edges.SlottedEdge(self, self.sy, be, slots=0.5 * hi),"f",
                     edges.SlottedEdge(self, self.sy[::-1], "f"), "f"]
            self.rectangularWall(y, hi, e, move="up")




