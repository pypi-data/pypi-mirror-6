#!/usr/bin/env python
import copy
import cv2
import math
import numpy
import os


def makedirs(p):
    try:
        os.makedirs(p)
    except OSError, e:
        if e.errno != 17:
            raise e


class ComicSlicer(object):
    def __init__(self, filename, img=None, min_size=(80, 100), max_size=(600, 800)):
        self.img = img
        if self.img is None:
            self.img = cv2.imread(filename)
        if self.img is None:
            raise Exception("no image found for %s" % filename)
        self.filename = filename
        if self.filename:
            self.filename = os.path.basename(filename)
        self.min_size = min_size
        self.max_size = max_size

    @staticmethod
    def dist(a, b):
        return abs(a - b)

    def _calc_inner_vertical_borders(self, transpose=False, min_size=80):
        if transpose:
            img = cv2.transpose(self.img)
        else:
            img = self.img
        height, width, depth = img.shape

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 80, 120)
        lines = cv2.HoughLinesP(edges, 1, math.pi, 10, None, 100, 1)

        borders = []
        if lines is None:
            return borders
        for line in lines[0]:
            a = line[1]
            b = line[3]
            offset = line[0]
            borders.append((offset, self.dist(a, b)))

        borders = sorted(borders)

        threshold = 16
        last_offset = 0
        last_group = [0]
        groups = [last_group]
        for offset, _ in borders:
            d = self.dist(offset, last_offset)
            if d > threshold:
                last_group = []
                groups.append(last_group)
            last_group.append(offset)
            last_offset = offset

        groups_condensed = []
        for group in groups:
            groups_condensed.append(int(numpy.mean(group)))

        inner_groups = []
        for group in groups_condensed:
            if self.dist(group, 0) < threshold:
                continue
            if self.dist(group, width) < threshold:
                continue
            inner_groups.append(group)

        big_enough = []
        last_group = 0
        for group in inner_groups:
            if self.dist(group, last_group) > min_size:
                big_enough.append(group)
                last_group = group

        return big_enough

    def calc_rows(self):
        return self._calc_inner_vertical_borders(transpose=True, min_size=140)

    def calc_cols(self):
        return self._calc_inner_vertical_borders()

    def calc_panel_filename(self, *numbers):
        prefix, ext = os.path.splitext(self.filename)
        if len(numbers) > 0:
            numbers = "_%s" % "_".join(["%02i" % number for number in numbers])
        else:
            numbers = ""
        return os.path.join(prefix, "%s%s%s" % (prefix, numbers, ext))

    def slice(self, target_dir="out"):
        panels = self.calc_panels()
        return self.slice_panels(panels, target_dir)

    def calc_panels(self):
        height, width, depth = self.img.shape
        if height > self.max_size[1]:
            ys = self.calc_rows()
        else:
            ys = []
        panels = []
        from_y = 0
        for nr_row, to_y in enumerate(ys + [height]):
            if width > self.max_size[0]:
                col_slicer = ComicSlicer(None, self.img[from_y:to_y, 0:width], min_size=self.min_size, max_size=self.max_size)
                xs = col_slicer.calc_cols()
            else:
                xs = []
            cols = []
            from_x = 0
            for nr_col, to_x in enumerate(xs + [width]):
                cols.append({
                    "type": "col",
                    "nr": nr_col,
                    "fromX": from_x,
                    "toX": to_x
                })
                from_x = to_x
            panels.append({
                "type": "row",
                "nr": nr_row,
                "fromY": from_y,
                "toY": to_y,
                "cols": cols
            })
            from_y = to_y
        return panels

    def mark_panels(self, panels, target_dir="out"):
        new_filename = os.path.join(target_dir, self.calc_panel_filename())
        makedirs(os.path.dirname(new_filename))
        img = copy.deepcopy(self.img)
        for row in panels:
            for col in row["cols"]:
                cv2.rectangle(img, (col["fromX"], row["fromY"]), (col["toX"], row["toY"]), (255, 0, 0), 3)
        cv2.imwrite(new_filename, img)
        return new_filename

    def slice_panels(self, panels, target_dir="out"):
        new_filenames = []
        for row in panels:
            for col in row["cols"]:
                new_filename = os.path.join(target_dir, self.calc_panel_filename(row["nr"], col["nr"]))
                new_filenames.append(new_filename)
                makedirs(os.path.dirname(new_filename))
                cv2.imwrite(new_filename, self.img[row["fromY"]:row["toY"], col["fromX"]:col["toX"]])
        return new_filenames


if __name__ == "__main__":
    import sys
    cs = ComicSlicer(sys.args[0])
    panels = cs.calc_panels()
    cs.mark_panels(panels, target_dir="out")
    cs.slice_panels(panels, target_dir="out")
