import os
import music21 as m21

DATASET_PATH = "deutschl/test"

ACCEPTABLE_DURATIONS = [0.25, 0.5, 0.75, 1., 1.5, 2., 3., 4.]


def load_songs(dataset_path):
    """
    Loads all kern songs in the dataset using music21.

    :param dataset_path: (str) Path to the dataset containing all songs
    :return songs: (list of m21 streams) List containing all songs
    """

    songs = []
    for path, subdirs, files in os.walk(dataset_path):  # go through all files in the dataset and load them

        # load songs using the m21 converter (only load krn files)
        songs = [m21.converter.parse(os.path.join(path, file)) for file in files if file[-4:] == ".krn"]
    return songs


def acceptable_duration(song, acceptable_durations):
    """
    Boolean to filter out the songs containing any not accepted durations.

    :param song: (m21 stream) The song to be tested for an acceptable duration
    :param acceptable_durations: (list of floats) List containing the acceptable durations in quarter length
    :return: (bool)
    """

    for note in song.flat.notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True


def transpose(song):
    """
    Transposes songs to C maj/A min depending on the song's mode

    :param song: (m21 stream) The song to be transposed
    :return: (m21 stream) Transposed version of the song
    """

    # get key from the song
    parts = song.getElementsByClass(m21.stream.Part)
    measures_first_part = parts[0].getElementByClass(m21.stream.Measure)
    key = measures_first_part[0][4]  # in this dataset: 4th item of the 1st measure of the score usually --> key

    # estimate key with m21 for songs missing key
    if not isinstance(key, m21.key.Key):
        key = song.analyse("key")

    # calculate interval for transposition
    if key.mode == "major":  # pieces in major modes --> transpose to C maj
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":  # pieces in minor modes --> transpose to A min
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))

    transposed_song = song.transpose(interval)

    return transposed_song


def preprocess(dataset_path):

    # load the songs
    print("Loading songs...")
    songs = load_songs(dataset_path)
    print(f"Loaded {len(songs)} songs from {DATASET_PATH}.")

    for song in songs:
        # filter out songs that have non-acceptable durations
        if not acceptable_duration(song, ACCEPTABLE_DURATIONS):
            continue

        # transpose songs with a major mode to C maj and songs with a minor mode to A min
        song = transpose(song)


preprocess(DATASET_PATH)
