from meta import plugin
from meta.navigation.movies import make_movie_item
from meta.info import get_tvshow_metadata_trakt, get_season_metadata_trakt, get_episode_metadata_trakt, \
    get_trakt_movie_metadata
from meta.navigation.base import get_icon_path
from meta.navigation.movies import make_movie_item
from meta.navigation.tvshows import make_tvshow_item, tv_play, tv_season
from language import get_string as _
from trakt import trakt

@plugin.route('/lists')
def lists():
    """ Lists directory """
    items = [
        {
            'label': _("Trakt liked lists"),
            'path': plugin.url_for("lists_trakt_liked_lists"),
            'icon': get_icon_path("tv"),  # TODO
        },
        {
            'label': _("Trakt my lists"),
            'path': plugin.url_for("lists_trakt_my_lists"),
            'icon': get_icon_path("tv"),  # TODO
        }
    ]
    return items

@plugin.route('/lists/trakt/liked_lists')
def lists_trakt_liked_lists():
    lists = trakt.trakt_get_liked_lists()
    items = []
    for list in lists:
        info = list["list"]
        name = info["name"]
        user = info["user"]["username"]
        slug = info["ids"]["slug"]
        items.append({
            'label': name,
            'path': plugin.url_for(lists_trakt_show_list, user = user, slug = slug),
            'icon': get_icon_path("tv"),  # TODO
        })
    return sorted(items,key = lambda item: item["label"])

@plugin.route('/lists/trakt/my_lists')
def lists_trakt_my_lists():
    lists = trakt.trakt_get_lists()
    items = []
    for list in lists:
        name = list["name"]
        user = list["user"]["username"]
        slug = list["ids"]["slug"]
        items.append({
            'label': name,
            'path': plugin.url_for(lists_trakt_show_list, user = user, slug = slug),
            'icon': get_icon_path("tv"),  # TODO
        })
    return sorted(items,key = lambda item: item["label"])

@plugin.route('/lists/trakt/show_list/<user>/<slug>')
def lists_trakt_show_list(user, slug):
    genres_dict = trakt.trakt_get_genres("tv")
    list_items = trakt.get_list(user, slug)
    items = []
    for list_item in list_items:
        item = None
        type = list_item["type"]

        if type == "show":
            tvdb_id = list_item["show"]["ids"]["tvdb"]
            show = list_item["show"]
            info = get_tvshow_metadata_trakt(show, genres_dict)

            context_menu = [
                (
                    _("Add to library"),
                    "RunPlugin({0})".format(plugin.url_for("tv_add_to_library", id=tvdb_id))
                ),
                (
                    _("Show info"), 'Action(Info)'
                )
            ]

            item = ({
                'label': info['title'],
                'path': plugin.url_for("tv_tvshow", id=tvdb_id),
                'context_menu': context_menu,
                'thumbnail': info['poster'],
                'icon': "DefaultVideo.png",
                'poster': info['poster'],
                'properties' : {'fanart_image' : info['fanart']},
                'info_type': 'video',
                'stream_info': {'video': {}},
                'info': info
            })

        elif type == "season":
            tvdb_id = list_item["show"]["ids"]["tvdb"]
            season = list_item["season"]
            show = list_item["show"]
            show_info = get_tvshow_metadata_trakt(show, genres_dict)
            season_info = get_season_metadata_trakt(show_info,season, genres_dict)
            label = "{0} - Season {1}".format(show["title"],season["number"])


            context_menu = [
                (
                    _("Add to library"),
                    "RunPlugin({0})".format(plugin.url_for("tv_add_to_library", id=tvdb_id))
                ),
                (
                    _("Show info"), 'Action(Info)'
                )
            ]

            item = ({
                'label': label,
                'path': plugin.url_for(tv_season, id=tvdb_id, season_num=list_item["season"]["number"]),
                'context_menu': context_menu,
                'info': season_info,
                'thumbnail': season_info['poster'],
                'icon': "DefaultVideo.png",
                'poster': season_info['poster'],
                'properties': {'fanart_image': season_info['fanart']},
            })

        elif type == "episode":
            tvdb_id = list_item["show"]["ids"]["tvdb"]

            episode = list_item["episode"]
            show = list_item["show"]

            season_number = episode["season"]
            episode_number = episode["number"]

            show_info = get_tvshow_metadata_trakt(show, genres_dict)
            episode_info = get_episode_metadata_trakt(show_info, episode)
            label = "{0} - S{1}E{2} - {3}".format(show_info["title"], season_number,
                                                  episode_number, episode_info["title"])

            context_menu = [
                (
                    _("Select stream..."),
                    "PlayMedia({0})".format(
                        plugin.url_for("tv_play", id=tvdb_id, season=season_number,
                                       episode=episode_number, mode='select'))
                ),
                (
                    _("Show info"),
                    'Action(Info)'
                )
            ]

            item = ({
                'label': label,
                'path': plugin.url_for("tv_play", id=tvdb_id, season=season_number,
                                       episode=episode_number, mode='default'),
                'context_menu': context_menu,
                'info': episode_info,
                'is_playable': True,
                'info_type': 'video',
                'stream_info': {'video': {}},
                'thumbnail': episode_info['poster'],
                'poster': episode_info['poster'],
                'icon': "DefaultVideo.png",
                'properties': {'fanart_image': episode_info['fanart']},
                      })

        elif type == "movie":
            movie = list_item["movie"]
            movie_info = get_trakt_movie_metadata(movie)

            item = make_movie_item(movie_info)

        if item is not None:
            items.append(item)
    return items