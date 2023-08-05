from __future__ import unicode_literals, print_function
from .exceptions import APIError


VALID_ENUM = {
    'AccessMask': [
        'None',
        'HideDateCreated',
        'HideDateModified',
        'HideDateTaken',
        'HideMetaData',
        'HideUserStats',
        'HideVisits',
        'NoCollections',
        'NoPrivateSearch',
        'NoPublicSearch',
        'NoRecentList',
        'ProtectExif',
        'ProtectXXLarge',
        'ProtectExtraLarge',
        'ProtectLarge',
        'ProtectMedium',
        'ProtectOriginals',
        'ProtectGuestbook',
        'NoPublicGuestbookPosts',
        'NoPrivateGuestbookPosts',
        'NoAnonymousGuestbookPosts',
        'ProtectComments',
        'NoPublicComments',
        'NoPrivateComments',
        'NoAnonymousComments',
        'PasswordProtectOriginals',
        'UnprotectCover',
        'ProtectAll',
    ],
    'AccessType': [
        'Private',
        'Public',
        'UserList',
        'Password',
    ],
    'InformationLevel': [
        'Level1',
        'Level2',
        'Full',
    ],
    'GroupShiftOrder': [
        'CreatedAsc',
        'CreatedDesc',
        'ModifiedAsc',
        'ModifiedDesc',
        'TitleAsc',
        'TitleDesc',
        'GroupsTop',
        'GroupsBottom',
    ],
    'PhotoSetType': [
        'Gallery',
        'Collection',
    ],
    'PhotoRotation': [
        'None',
        'Rotate90',
        'Rotate180',
        'Rotate270',
        'Flip',
        'Rotate90Flip',
        'Rotate180Flip',
        'Rotate270Flip',
    ],
    'ShiftOrder': [
        'CreatedAsc',
        'CreatedDesc',
        'TakenAsc',
        'TakenDesc',
        'TitleAsc',
        'TitleDesc',
        'SizeAsc',
        'SizeDesc',
        'FileNameAsc',
        'FileNameDesc',
    ],
    'SortOrder': [
        'Date',
        'Popularity',
        'Rank',
    ],
    'VideoPlaybackMode': [
        'Flash',
        'iOS',
        'Http',
    ],
}
VALID_OBJECTS = {
    'AccessUpdater': {
        'AccessMask': 'AccessMask',
        'AccessType': 'AccessType',
        'Viewers': None,
        'Password': None,
        'IsDerived': None,
        'PasswordHint': None,
    },
    'GroupUpdater': {
        'Title': None,
        'Caption': None,
        'CustomReference': None,
    },
    'PhotoSetUpdater': {
        'Title': None,
        'Caption': None,
        'Keywords': None,
        'Categories': None,
        'CustomReference': None,
    },
    'PhotoUpdater': {
        'Title': None,
        'Caption': None,
        'Keywords': None,
        'Categories': None,
        'Copyright': None,
        'Filename': None,
    },
    'MessageUpdater': {
        'PosterName': None,
        'PosterUrl': None,
        'PosterEmail': None,
        'Body': None,
        'IsPrivate': None,
    },
}


def assert_type(value, expected_type, param, method):
    if value['$type'] != expected_type:
        raise APIError('Got `{0}` instead of `{1}` value for `{2}` for `{3}` method.'
                       ''.format(value['$type'], expected_type, param, method))


def validate_value(value, data_struct, method):
    if value not in VALID_ENUM[data_struct]:
        raise APIError('`{0}` is an invalid value for `{1}` enumeration for `{2}` method.'
                       ''.format(value, data_struct, method))


def validate_object(value, data_struct, method):
    if not isinstance(value, dict):
        raise APIError('`{0}` must be a dict for `{1}` method.'
                       ''.format(data_struct, method))

    for k, v in value.items():
        if k not in VALID_OBJECTS[data_struct]:
            raise APIError('`{0}` is an invalid key for `{1}` object for `{2}` method.'
                           ''.format(value, data_struct, method))
        enum = VALID_OBJECTS[data_struct][k]
        if enum is not None:
            validate_value(v, enum, method)
