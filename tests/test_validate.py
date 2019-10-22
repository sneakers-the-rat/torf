import torf

import pytest
import os


def test_length_and_files_in_info(generated_multifile_torrent):
    t = generated_multifile_torrent
    t.metainfo['info']['length'] = 123
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == "Invalid metainfo: ['info'] includes both 'length' and 'files'"


def test_wrong_name_type(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    t.metainfo['info']['name'] = 123
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['name'] "
                                  "must be str, not int: 123")

def test_wrong_piece_length_type(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    t.metainfo['info']['piece length'] = [700]
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['piece length'] "
                                  "must be int, not list: [700]")

def test_wrong_pieces_type(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    t.metainfo['info']['pieces'] = 'many'
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['pieces'] "
                                  "must be bytes or bytearray, not str: 'many'")

def test_pieces_is_empty(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    t.metainfo['info']['pieces'] = bytes()
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == "Invalid metainfo: ['info']['pieces'] is empty"

def test_invalid_number_of_bytes_in_pieces(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    for i in range(1, 10):
        t.metainfo['info']['pieces'] = bytes(os.urandom(i*20))
        t.validate()

        for j in ((i*20)+1, (i*20)-1):
            t.metainfo['info']['pieces'] = bytes(os.urandom(j))
            with pytest.raises(torf.MetainfoError) as excinfo:
                t.validate()
            assert str(excinfo.value) == ("Invalid metainfo: length of ['info']['pieces'] "
                                          "is not divisible by 20")


def test_no_announce_is_ok(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    if 'announce' in t.metainfo:
        del t.metainfo['announce']
    t.validate()

def test_wrong_announce_type(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    for typ in (bytearray, list, tuple):
        t.metainfo['announce'] = typ()
        with pytest.raises(torf.MetainfoError) as excinfo:
            t.validate()
        assert str(excinfo.value) == (f"Invalid metainfo: ['announce'] "
                                      f"must be str, not {typ.__qualname__}: {t.metainfo['announce']}")

def test_invalid_announce_url(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    for url in ('123', 'http://123:xxx/announce'):
        t.metainfo['announce'] = url
        with pytest.raises(torf.MetainfoError) as excinfo:
            t.validate()
        assert str(excinfo.value) == f"Invalid metainfo: ['announce'] is invalid: {url!r}"

def test_no_announce_list_is_ok(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    if 'announce-list' in t.metainfo:
        del t.metainfo['announce-list']
    t.validate()

def test_wrong_announce_list_type(generated_singlefile_torrent):
    t = generated_singlefile_torrent

    # announce-list must be a list
    for typ in (bytearray, str):
        t.metainfo['announce-list'] = typ()
        with pytest.raises(torf.MetainfoError) as excinfo:
            t.validate()
        assert str(excinfo.value) == (f"Invalid metainfo: ['announce-list'] "
                                      f"must be list, not {typ.__qualname__}: {t.metainfo['announce-list']!r}")

    # Each item in announce-list must be a list
    for typ in (bytearray, set):
        tier = typ()
        for lst in ([tier],
                    [tier, []],
                    [[], tier],
                    [[], tier, []]):
            t.metainfo['announce-list'] = lst
            with pytest.raises(torf.MetainfoError) as excinfo:
                t.validate()
            tier_index = lst.index(tier)
            assert str(excinfo.value) == (f"Invalid metainfo: ['announce-list'][{tier_index}] "
                                          f"must be list, not {typ.__qualname__}: {tier!r}")

    # Each item in each list in announce-list must be a string
    for typ in (bytearray, set):
        url = typ()
        for tier in ([url],
                     ['http://localhost:123/', url],
                     [url, 'http://localhost:123/'],
                     ['http://localhost:123/', url, 'http://localhost:456/']):
            url_index = tier.index(url)
            for lst in ([tier],
                        [tier, []],
                        [[], tier],
                        [[], tier, []]):
                tier_index = lst.index(tier)
                t.metainfo['announce-list'] = lst
                with pytest.raises(torf.MetainfoError) as excinfo:
                    t.validate()
                assert str(excinfo.value) == (f"Invalid metainfo: ['announce-list'][{tier_index}][{url_index}] "
                                              f"must be str, not {typ.__qualname__}: {url!r}")

def test_invalid_url_in_announce_list(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    for url in ('123', 'http://123:xxx/announce'):
        for tier in ([url],
                     ['http://localhost:123/', url],
                     [url, 'http://localhost:123/'],
                     ['http://localhost:123/', url, 'http://localhost:456/']):
            url_index = tier.index(url)
            for lst in ([tier],
                        [tier, []],
                        [[], tier],
                        [[], tier, []]):
                tier_index = lst.index(tier)
                t.metainfo['announce-list'] = lst
                with pytest.raises(torf.MetainfoError) as excinfo:
                    t.validate()
                assert str(excinfo.value) == (f"Invalid metainfo: ['announce-list'][{tier_index}][{url_index}] "
                                              f"is invalid: {url!r}")

def test_no_announce_and_no_announce_list_when_torrent_is_private(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    t.metainfo['info']['private'] = True
    if 'announce' in t.metainfo:
        del t.metainfo['announce']
    if 'announce-list' in t.metainfo:
        del t.metainfo['announce-list']
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['private'] is True "
                                  "but no announce URLs are specified")

    t.metainfo['announce'] = 'http://foo.bar'
    t.validate()

    del t.metainfo['announce']
    t.metainfo['announce-list'] = [['http://foo.bar']]
    t.validate()


def test_singlefile_wrong_length_type(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    t.metainfo['info']['length'] = 'foo'
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['length'] "
                                  "must be int or float, not str: 'foo'")

def test_singlefile_wrong_md5sum_type(generated_singlefile_torrent):
    t = generated_singlefile_torrent
    t.metainfo['info']['md5sum'] = 0
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['md5sum'] "
                                  "must be str, not int: 0")

    t.metainfo['info']['md5sum'] = 'Z8b329da9893e34099c7d8ad5cb9c940'
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['md5sum'] is invalid: "
                                  "'Z8b329da9893e34099c7d8ad5cb9c940'")


def test_multifile_wrong_files_type(generated_multifile_torrent):
    t = generated_multifile_torrent
    t.metainfo['info']['files'] = 'foo'
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['files'] "
                                  "must be list, not str: 'foo'")

def test_multifile_wrong_path_type(generated_multifile_torrent):
    t = generated_multifile_torrent
    t.metainfo['info']['files'][0]['path'] = 'foo/bar/baz'
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['files'][0]['path'] "
                                  "must be list, not str: 'foo/bar/baz'")

def test_multifile_wrong_path_item_type(generated_multifile_torrent):
    t = generated_multifile_torrent
    t.metainfo['info']['files'][1]['path'][0] = 17
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['files'][1]['path'][0] "
                                  "must be str, not int: 17")

def test_multifile_wrong_length_type(generated_multifile_torrent):
    t = generated_multifile_torrent
    t.metainfo['info']['files'][2]['length'] = ['this', 'is', 'not', 'a', 'length']
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['files'][2]['length'] "
                                  "must be int or float, not list: ['this', 'is', 'not', 'a', 'length']")

def test_multifile_wrong_md5sum_type(generated_multifile_torrent):
    t = generated_multifile_torrent
    t.metainfo['info']['files'][0]['md5sum'] = 0
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['files'][0]['md5sum'] "
                                  "must be str, not int: 0")

    t.metainfo['info']['files'][0]['md5sum'] = 'Z8b329da9893e34099c7d8ad5cb9c940'
    with pytest.raises(torf.MetainfoError) as excinfo:
        t.validate()
    assert str(excinfo.value) == ("Invalid metainfo: ['info']['files'][0]['md5sum'] is invalid: "
                                  "'Z8b329da9893e34099c7d8ad5cb9c940'")


def assert_missing_metainfo(torrent, *keys):
    md = torrent.metainfo
    for key in keys[:-1]:
        md = md[key]
    del md[keys[-1]]
    with pytest.raises(torf.MetainfoError) as excinfo:
        torrent.dump()
    assert excinfo.match(rf"Invalid metainfo: Missing {keys[-1]!r} in \['info'\]")

def test_singlefile_missing_info_path(generated_singlefile_torrent):
    assert_missing_metainfo(generated_singlefile_torrent, 'info', 'name')

def test_singlefile_missing_info_piece_length(generated_singlefile_torrent):
    assert_missing_metainfo(generated_singlefile_torrent, 'info', 'piece length')

def test_singlefile_missing_info_pieces(generated_singlefile_torrent):
    assert_missing_metainfo(generated_singlefile_torrent, 'info', 'pieces')

def test_multifile_missing_info_path(generated_multifile_torrent):
    assert_missing_metainfo(generated_multifile_torrent, 'info', 'name')

def test_multifile_missing_info_piece_length(generated_multifile_torrent):
    assert_missing_metainfo(generated_multifile_torrent, 'info', 'piece length')

def test_multifile_missing_info_pieces(generated_multifile_torrent):
    assert_missing_metainfo(generated_multifile_torrent, 'info', 'pieces')

def test_multifile_missing_info_files_0_length(generated_multifile_torrent):
    assert_missing_metainfo(generated_multifile_torrent, 'info', 'files', 0, 'length')

def test_multifile_missing_info_files_1_length(generated_multifile_torrent):
    assert_missing_metainfo(generated_multifile_torrent, 'info', 'files', 1, 'length')

def test_multifile_missing_info_files_1_path(generated_multifile_torrent):
    assert_missing_metainfo(generated_multifile_torrent, 'info', 'files', 1, 'path')

def test_multifile_missing_info_files_2_path(generated_multifile_torrent):
    assert_missing_metainfo(generated_multifile_torrent, 'info', 'files', 2, 'path')


def assert_mismatching_filesizes(torrent, *args):
    value = args[-1]
    keys = args[:-1]
    md = torrent.metainfo
    for key in keys[:-1]:
        md = md[key]
    orig_value = md[keys[-1]]
    md[keys[-1]] = value
    with pytest.raises(torf.MetainfoError) as excinfo:
        torrent.dump()
    assert excinfo.match(r"Invalid metainfo: Mismatching file sizes in metainfo \(\d+\) "
                         rf"and local file system \(\d+\): '{torrent.path}")

def test_singlefile_mismatching_filesize(generated_singlefile_torrent):
    assert_mismatching_filesizes(generated_singlefile_torrent,
                                 'info', 'length', 12345)

def test_multifile_mismatching_filesize(generated_multifile_torrent):
    assert_mismatching_filesizes(generated_multifile_torrent,
                                 'info', 'files', 1, 'length', 12345)
