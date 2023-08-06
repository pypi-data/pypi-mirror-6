
import imdb


i = imdb.IMDb()

SERIES_ID = '0898266'
series = i.get_movie(SERIES_ID)

i.update(series, 'episodes')


# overall list of characters
# (indexed by character name)
characters = {}

charactersPerEpisode = {}

for seasonNumber, episodes in series['episodes'].iteritems():

    charactersPerEpisode[seasonNumber] = {}

    for episodeNumber, episode in episodes.iteritems():

        print '==== Season {season} - Episode {episode} ===='.format(
            season=seasonNumber, episode=episodeNumber)

        charactersPerEpisode[seasonNumber][episodeNumber] = []

        i.update(episode, 'all')
        cast = episode['cast']
        for person in cast:

            character = person.currentRole
            name = character['name']
            if name not in characters:
                i.update(character, 'all')
                characters[name] = character

            charactersPerEpisode[seasonNumber][episodeNumber].append(name)
