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
            trakt_id = list_item["show"]["ids"]["trakt"]
            tvshow = trakt.get_show(trakt_id)
            item = make_tvshow_item(get_tvshow_metadata_trakt(tvshow, genres_dict))

        elif type == "season":
            tvdb_id = list_item["show"]["ids"]["tvdb"]
            trakt_id = list_item["show"]["ids"]["trakt"]
            tvshow = trakt.get_show(trakt_id)
            tvshow_info = get_tvshow_metadata_trakt(tvshow, genres_dict)
            season = trakt.get_season(trakt_id,list_item["season"]["number"])
            season_info = get_season_metadata_trakt(tvshow_info, season)
            label = "{0} - Season {1}".format(tvshow_info["title"],season_info["season"])


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
                'info': tvshow_info,
                'thumbnail': season_info['poster'],
                'icon': "DefaultVideo.png",
                'poster': season_info['poster'],
                'properties': {'fanart_image': season_info['fanart']},
            })

        elif type == "episode":
            trakt_id = list_item["show"]["ids"]["trakt"]
            tvdb_id = list_item["show"]["ids"]["tvdb"]

            season_number = list_item["episode"]["season"]
            episode_number = list_item["episode"]["number"]

            tvshow = trakt.get_show(trakt_id)
            tvshow_info = get_tvshow_metadata_trakt(tvshow, genres_dict)
            season = trakt.get_season(trakt_id, season_number)
            season_info = get_season_metadata_trakt(tvshow_info, season)
            episode = trakt.get_episode(trakt_id,season_number, episode_number)
            episode_info = get_episode_metadata_trakt(season_info, episode)
            label = "{0} - S{1}E{2} - {3}".format(tvshow_info["title"], season_number,
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
            trakt_id = list_item["movie"]["ids"]["trakt"]
            trakt_movie = trakt.get_movie(trakt_id)
            movie_info = get_trakt_movie_metadata(trakt_movie)

            item = make_movie_item(movie_info)

        if item is not None:
            items.append(item)
    return items