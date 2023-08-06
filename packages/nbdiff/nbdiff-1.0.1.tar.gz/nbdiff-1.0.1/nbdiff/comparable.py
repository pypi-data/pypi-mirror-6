from .diff import (
    diff,
    create_grid,
    find_matches,
)
import Levenshtein


class BooleanPlus(object):

    def __init__(self, truthfulness, mod):
        self.truth = truthfulness
        self.modified = mod

    def __nonzero__(self):
        '''
        for evaluating as a boolean
        '''
        return self.truth

    def is_modified(self):
        return self.modified


class LineComparator(object):

    def __init__(self, data, check_modified=False):
        self.data = data
        self.check_modified = check_modified

    def __eq__(self, other):
        return self.equal(self.data, other.data)

    def equal(self, line1, line2):
        '''
        return true if exactly equal or if equal but modified,
        otherwise return false
        return type: BooleanPlus
        '''

        eqLine = line1 == line2
        if eqLine:
            return BooleanPlus(True, False)
        else:
            unchanged_count = self.count_similar_words(line1, line2)
            similarity_percent = (
                (2.0 * unchanged_count) /
                (len(line1.split()) + len(line2.split()))
            )
            if similarity_percent >= 0.50:
                return BooleanPlus(True, True)
            return BooleanPlus(False, False)

    def count_similar_words(self, line1, line2):
        words1 = line1.split()
        words2 = line2.split()
        grid = create_grid(words1, words2)
        matches = []

        for colnum in range(len(grid)):
            new_matches = find_matches(grid[colnum], colnum)
            matches = matches + new_matches

        matched_cols = [r[0] for r in matches]
        matched_rows = [r[1] for r in matches]
        unique_cols = set(matched_cols)
        unique_rows = set(matched_rows)

        return min(len(unique_cols), len(unique_rows))


class CellComparator():

    def __init__(self, data, check_modified=False):
        self.data = data
        self.check_modified = check_modified

    def __eq__(self, other):
        return self.equal(self.data, other.data)

    def equal(self, cell1, cell2):
        if not cell1["cell_type"] == cell2["cell_type"]:
            return False
        elif cell1["cell_type"] == "heading":
            if not cell1["level"] == cell2["level"]:
                return False
            else:
                if cell1['source'] == cell2['source']:
                    return True
                result = diff(
                    cell1["source"].split(' '),
                    cell2["source"].split(' ')
                )
                modified = 0.0
                unchanged = 0.0
                for dict in result:
                    if dict['state'] == "added" or dict['state'] == "deleted":
                        modified += 1
                    elif dict['state'] == "unchanged":
                        unchanged += 1
                modifiedness = unchanged/(modified + unchanged)
                if modifiedness >= 0.6:
                    return BooleanPlus(True, True)
                else:
                    return False
        elif self.istextcell(cell1):
            return cell1["source"] == cell2["source"]
        else:
            return self.compare_cells(cell1, cell2)

    def istextcell(self, cell):
        return "source" in cell

    def equaloutputs(self, output1, output2):
        if not len(output1) == len(output2):
            return False
        for i in range(0, len(output1)):
            if not output1[i] == output2[i]:
                return False
        return True

    def compare_cells(self, cell1, cell2):
        '''
        return true if exactly equal or if equal but modified,
        otherwise return false
        return type: BooleanPlus
        '''
        eqlanguage = cell1["language"] == cell2["language"]
        eqinput = cell1["input"] == cell2["input"]
        eqoutputs = self.equaloutputs(cell1["outputs"], cell2["outputs"])

        if eqlanguage and eqinput and eqoutputs:
            return BooleanPlus(True, False)
        elif not self.check_modified:
            return BooleanPlus(False, False)

        input1 = u"".join(cell1['input'])
        input2 = u"".join(cell2['input'])
        similarity_percent = Levenshtein.ratio(input1, input2)
        if similarity_percent >= 0.65:
            return BooleanPlus(True, True)
        return BooleanPlus(False, False)
