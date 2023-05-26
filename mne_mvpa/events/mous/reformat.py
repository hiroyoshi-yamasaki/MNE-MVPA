import re
from typing import Union, Tuple

import numpy as np
import pandas as pd


########################################################################################################################
# Mother of Unification Study                                                                                          #
########################################################################################################################


########################################################################################################################
# Final CSV file format                                                                                                #
#                                                                                                                      #
# `sample` (int): original sample index                                                                                #
# `onset` (float): onset time in seconds                                                                               #
# `duration` (float): duration of the event in seconds                                                                 #
# `type` (str): 'block', 'fixation', 'ISI', 'pause', 'question', 'response', 'word'                                    #
# `value` (str):                                                                                                       #
#   `type` == 'block': 'WOORDEN'/'ZINNEN'                                                                              #
#   `type` == 'fixation'/'ISI'/'pause'/: NaN                                                                           #
#   `type` == 'question': question number                                                                              #
#   `type` == 'response': '1'/'2'/'3'                                                                                  #
#   `type` == 'word': token                                                                                            #
# `sentence` (bool): true if sentence, false if word list                                                              #
# `relative_clause` (bool): true if it contains relative clause, false if it doesn't                                   #
# `target`: true if it is the target word, false if not                                                                #
########################################################################################################################


def combine_visual(events: np.array, df: pd.DataFrame, tolerance: int = 2) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Combine events array generated with MNE-python `mne.find_events()` with TSV file provided with the MOUS data.
    The two sets of events are compared and checked for inconsistencies. Inconsistent events are logged in dataframe
    and returned. There are two kinds of errors:
    - types and values of the events don’t match -> logged info [index, sample, type, value]
    - sampling value differ by more than `tolerance` -> logged info [index, sample, 'sample_diff', diff]
    :param events: events array provided by `mne.find_events()`
    :param df: dataframe from TSV file
    :param tolerance: max. tolerated number of sampling cycles to differ by, default = 2
    :return:
        events_df: [sample, onset, duration, type, value, sentence, relative_clause, target]
        error_df: [index, onset, sample, type, value]
    """

    events_list = []    # [sample, onset, duration, type, value, sentence, relative_clause, target]
    error_list = []     # [index, onset, sample, type, value, trigger_value]
    for idx, row in df.iterrows():

        if not isinstance(row["value"], str):  # skip NaN
            continue

        # Ignore these
        if row["type"] in ["trial", "frontpanel trigger", "UPPT001", "UPPT002"]:
            continue
        if row["value"] == "blank":
            continue

        # Find an event with the closest sample number
        nearest_idx = np.abs(events[:, 0] - row["sample"]).argmin()
        sample, _, value = events[nearest_idx]

        # The sample value deviates from each other
        diff = abs(sample - row["sample"])
        if diff > tolerance:
            error_list.append([idx, row["sample"], "sample_diff", diff])

        # Words or response
        if value in [1, 2, 3]:
            event = _handle_1_3(row, value)

        # Words
        elif value in [4, 5, 6, 7, 8]:
            event = _handle_4_8(row, value)

        # Mini-block start
        elif value == 10:
            event = _handle_10(row)

        # ISI
        elif value == 15:
            event = _handle_15(row)

        # Fixation
        elif value == 20:
            event = _handle_20(row)

        # Pause
        elif value == 30:
            event = _handle_30(row)

        # Question
        elif value == 40:
            event = _handle_40(row)

        # Response 1
        elif value == 16:
            event = _handle_16(row)

        # Response 2
        elif value == 32:
            event = _handle_32(row)

        # UDIO001
        elif value == 128:

            if row["type"] == "UDIO001":  # ignore this one
                continue
            else:
                event = None
        else:
            raise ValueError(f"Unknown trigger value {value}")

        if event is not None:
            events_list.append(event)
        else:
            error_list.append([idx, row["sample"], row["onset"], row["type"], row["value"], value])

    events_df = pd.DataFrame(events_list, columns=["sample", "onset", "duration", "type", "value", "sentence",
                                                   "relative_clause", "target"])
    errors_df = pd.DataFrame(error_list, columns=["index", "onset", "sample", "type", "value", "trigger_value"])

    # Set dtypes
    events_df["duration"] = events_df["duration"].astype(float)

    return events_df, errors_df


def _handle_1_3(row: pd.Series, value: int) -> Union[None, Tuple[float, float, float, str, str, bool, bool, bool]]:
    """
    Trigger values 1-3 are word conditions: '- onset of individual word, including the word identity, the corresponding
    trigger value, and the intended length in milliseconds'

    or response 1-3 (for visual condition, corresponds to 11-13 in auditory condition)

    :param row: event row from TSV file
    :param value:
    :return:
        None: (if invalid) or
        an event: [sample, onset, duration, 'word/response', word/1/2/3, sentence, relative_clause, target]
    """

    value = str(value)

    # Word
    if row["type"] == "Picture" and row["value"][0] == value:

        if value == "1":
            sentence, relative_clause, target = True, True, False
        elif value == "2":
            sentence, relative_clause, target = True, True, True
        elif value == "3":
            sentence, relative_clause, target = False, True, False
        else:
            raise ValueError(f"Invalid value {value} (should be between 1 and 3)")

        match1 = re.match(r"\d\s*(\d+)\s*", row["value"])               # e.g. 5 300
        match2 = re.match(r"\d\s*([\w.\']+)\s*(\d+)\s*", row["value"])  # e.g. 5 gemene 300
        if match1:
            word = "<END>"
            duration = match1.group(1)

        elif match2:
            word = match2.group(1)
            duration = match2.group(2)
        else:
            raise ValueError(f"The 'value' '{row['value']}' is not matched. (should be of the format"
                             f" digit word duration")

        return row["sample"], row["onset"], duration, "word", word, sentence, relative_clause, target

    # Response
    elif row["type"] == "Response" and row["value"][0] == value:

        sentence, relative_clause, target = False, False, False
        return row["sample"], row["onset"], row["duration"], "response", value, sentence, relative_clause, target

    # No match
    else:
        return None


def _handle_4_8(row: pd.Series, value: int) -> Union[None, Tuple[float, float, float, str, str, bool, bool, bool]]:
    """
    Trigger values 4-8 are word conditions: '- onset of individual word, including the word identity, the corresponding
    trigger value, and the intended length in milliseconds'
    :param row: event row from TSV file
    :param value: value according to the events array
    :return:
        None: (if invalid) or
        an event: [sample, onset, duration, 'word', word, sentence, relative_clause, target]
    """

    value = str(value)

    # Word
    if row["type"] == "Picture" and row["value"][0] == value:

        if value == "4":
            sentence, relative_clause, target = False, True, True
        elif value == "5":
            sentence, relative_clause, target = True, False, False
        elif value == "6":
            sentence, relative_clause, target = True, False, True
        elif value == "7":
            sentence, relative_clause, target = False, False, False
        elif value == "8":
            sentence, relative_clause, target = False, False, True
        else:
            raise ValueError(f"Invalid value {value} (should be between 4 and 8)")

        match1 = re.match(r"\d\s*(\d+)\s*", row["value"])               # sentence final, e.g. 5 300
        match2 = re.match(r"\d\s*([\w.\']+)\s*(\d+)\s*", row["value"])  # other words, e.g. 5 gemene 300

        if match1:
            word = "<END>"
            duration = match1.group(1)

        elif match2:
            word = match2.group(1)
            duration = match2.group(2)
        else:
            raise ValueError(f"The 'value' '{row['value']}' is not matched. (should be of the format"
                             f" digit word duration")


        return row["sample"], row["onset"], duration, "word", word, sentence, relative_clause, target

    # No match
    else:
        return None


def _handle_10(row: pd.Series) -> Union[None, Tuple[float, float, float, str, str, bool, bool, bool]]:
    """
    Trigger value 10 is mini-block onset: '- onset of mini-block condition'
    :param row: event row from TSV file
    :return:
        None: (if invalid) or
        an event: [sample, onset, duration, 'block', 'WOORDEN/ZINNEN', False, False, False]
    """

    if row["type"] == "Picture" and row["value"] in ["WOORDEN", "ZINNEN"]:
        return row["sample"], row["onset"], row["duration"], "block", row["value"], False, False, False

    else:
        return None


def _handle_15(row: pd.Series) -> Union[None, Tuple[float, float, float, str, str, bool, bool, bool]]:
    """
    Trigger value 15 is inter-stimulus interval (ISI): '- onset of inter-stimulus interval'
    :param row: event row from TSV file
    :return:
        None: (if invalid) or
        an event: [sample, onset, duration, 'ISI', 'NA', False, False, False]
    """

    if row["type"] == "Picture" and row["value"] == "ISI":
        return row["sample"], row["onset"], row["duration"], "ISI", "NA", False, False, False
    else:
        return None


def _handle_20(row: pd.Series) -> Union[None, Tuple[float, float, float, str, str, bool, bool, bool]]:
    """
    Trigger value 20 is fixation: '- onset of fixation cross on the screen with intended duration'
    :param row: event row from TSV file
    :return:
        None: (if invalid) or
        an event: [sample, onset, duration, 'fixation', 'NA', False, False, False]
    """

    if row["type"] == "Picture" and row["value"].startswith("FIX"):

        match = re.match(r"FIX\s*(\d+)\s*", row["value"])  # e.g. FIX 3948

        if not match:
            raise ValueError(f"The 'value' {row['value']} is not matched. (should be of the format"
                             f" FIX duration")

        duration = match.group(1)

        return row["sample"], row["onset"], duration, "fixation", "NA", False, False, False

    else:
        return None


def _handle_30(row: pd.Series) -> Union[None, Tuple[float, float, float, str, str, bool, bool, bool]]:
    """
    Trigger value 30 is pause: 'onset of a pause between blocks'
    :param row: event row from TSV file
    :return:
        None: (if invalid) or
        an event: [sample, onset, duration, 'pause', 'NA', False, False, False]
    """

    if row["type"] == "Picture" and row["value"] == "pause":

        return row["sample"], row["onset"], row["duration"], "pause", "NA", False, False, False
    else:
        return None


def _handle_40(row: pd.Series) -> Union[None, Tuple[float, float, float, str, str, bool, bool, bool]]:
    """
    Trigger value 40 is question: '- onset of question with identity of the question, matching the question in
    the stimuli presentation code' (from the paper)
    :param row: event row from TSV file
    :return:
        None: (if invalid) or
        an event: [sample, onset, duration, 'question', code, False, False, False]
    """

    if row["type"] == "Picture" and row["value"].startswith("QUESTION"):

        match = re.match(r"QUESTION\s*(\d+)\s*", row["value"])  # e.g. QUESTION 341

        if not match:
            raise ValueError(f"The 'value' '{row['value']}' is not matched. (should be of the format"
                             f" QUESTION duration")

        code = match.group(1)  # presentation code

        return row["sample"], row["onset"], row["duration"], "question", code, False, False, False
    else:
        return None


def _handle_16(row: pd.Series) -> Union[None, Tuple[float, float, float, str, str, bool, bool, bool]]:
    """
    Trigger value 16 (not documented) seems to correspond to 'response' with value '1'
    :param row: event row from TSV file
    :return:
        None: (if invalid) or
        an event: [sample, onset, duration, 'response', '1', False, False, False]
    """


    if row["type"] == "Response" and row["value"] == "1":
        return row["sample"], row["onset"], row["duration"], "response", "1", False, False, False
    else:
        return None


def _handle_32(row: pd.Series) -> Union[None, Tuple[float, float, float, str, str, bool, bool, bool]]:
    """
    Trigger value 32 (not documented) seems to correspond to 'response' with value '2'
    :param row: event row from TSV file
    :return:
        None: (if invalid) or
        an event: [sample, onset, duration, 'response', '2', False, False, False]
    """

    if row["type"] == "Response" and row["value"] == "2":
        return row["sample"], row["onset"], row["duration"], "response", "2", False, False, False
    else:
        return None
