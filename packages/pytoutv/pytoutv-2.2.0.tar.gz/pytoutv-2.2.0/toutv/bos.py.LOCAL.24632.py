# Copyright (c) 2012, Benjamin Vanheuverzwijn <bvanheu@gmail.com>
# All rights reserved.
#
# Thanks to Marc-Etienne M. Leveille
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
import os
import datetime
import toutv.dl


class AbstractEmission:
    def get_id(self):
        return self.Id

    def get_genre(self):
        return self.Genre

    def get_url(self):
        return self.Url

    def get_removal_date(self):
        if self.DateRetraitOuEmbargo is None:
            return None

        # Format looks like: /Date(1395547200000-0400)/
        d = self.DateRetraitOuEmbargo
        m = re.match(r'/Date\((\d+)-\d+\)/', d)
        if m is not None:
            ts = int(m.group(1)) // 1000

            return datetime.datetime.fromtimestamp(ts)

        return None

    def __str__(self):
        return '{} ({})'.format(self.get_title(), self.get_id())


class Emission(AbstractEmission):
    def __init__(self):
        self.CategoryURL = None
        self.ClassCategory = None
        self.ContainsAds = None
        self.Country = None
        self.DateRetraitOuEmbargo = None
        self.Description = None
        self.DescriptionOffline = None
        self.DescriptionUnavailable = None
        self.DescriptionUnavailableText = None
        self.DescriptionUpcoming = None
        self.DescriptionUpcomingText = None
        self.EstContenuJeunesse = None
        self.EstExclusiviteRogers = None
        self.GeoTargeting = None
        self.Genre = None
        self.Id = None
        self.ImageBackground = None
        self.ImagePromoLargeI = None
        self.ImagePromoLargeJ = None
        self.ImagePromoNormalK = None
        self.Network = None
        self.Network2 = None
        self.Network3 = None
        self.ParentId = None
        self.Partner = None
        self.PlaylistExist = None
        self.PromoDescription = None
        self.PromoTitle = None
        self.RelatedURL1 = None
        self.RelatedURL2 = None
        self.RelatedURL3 = None
        self.RelatedURL4 = None
        self.RelatedURL5 = None
        self.RelatedURLImage1 = None
        self.RelatedURLImage2 = None
        self.RelatedURLImage3 = None
        self.RelatedURLImage4 = None
        self.RelatedURLImage5 = None
        self.RelatedURLText1 = None
        self.RelatedURLText2 = None
        self.RelatedURLText3 = None
        self.RelatedURLText4 = None
        self.RelatedURLText5 = None
        self.SeasonNumber = None
        self.Show = None
        self.ShowSearch = None
        self.SortField = None
        self.SortOrder = None
        self.SubCategoryType = None
        self.Title = None
        self.TitleIndex = None
        self.Url = None
        self.Year = None

    def get_title(self):
        return self.Title

    def get_year(self):
        return self.Year

    def get_country(self):
        return self.Country

    def get_description(self):
        return self.Description

    def get_network(self):
        return self.Network

    def get_tags(self):
        tags = []
        if self.EstExclusiviteRogers:
            tags.append('rogers')
        if self.EstContenuJeunesse:
            tags.append('youth')

        return tags


class Genre:
    def __init__(self):
        self.CategoryURL = None
        self.ClassCategory = None
        self.Description = None
        self.Id = None
        self.ImageBackground = None
        self.ParentId = None
        self.Title = None
        self.Url = None

    def get_id(self):
        return self.Id

    def get_title(self):
        return self.Title

    def __str__(self):
        return '{} ({})'.format(self.get_title(), self.get_id())


class Episode:
    def __init__(self):
        self.AdPattern = None
        self.AirDateFormated = None
        self.AirDateLongString = None
        self.Captions = None
        self.CategoryId = None
        self.ChapterStartTimes = None
        self.ClipType = None
        self.Copyright = None
        self.Country = None
        self.DateSeasonEpisode = None
        self.Description = None
        self.DescriptionShort = None
        self.EpisodeNumber = None
        self.EstContenuJeunesse = None
        self.Event = None
        self.EventDate = None
        self.FullTitle = None
        self.GenreTitle = None
        self.Id = None
        self.ImageBackground = None
        self.ImagePlayerLargeA = None
        self.ImagePlayerNormalC = None
        self.ImagePromoLargeI = None
        self.ImagePromoLargeJ = None
        self.ImagePromoNormalK = None
        self.ImageThumbMicroG = None
        self.ImageThumbMoyenL = None
        self.ImageThumbNormalF = None
        self.IsMostRecent = None
        self.IsUniqueEpisode = None
        self.Keywords = None
        self.LanguageCloseCaption = None
        self.Length = None
        self.LengthSpan = None
        self.LengthStats = None
        self.LengthString = None
        self.LiveOnDemand = None
        self.MigrationDate = None
        self.Musique = None
        self.Network = None
        self.Network2 = None
        self.Network3 = None
        self.NextEpisodeDate = None
        self.OriginalAirDate = None
        self.PID = None
        self.Partner = None
        self.PeopleAuthor = None
        self.PeopleCharacters = None
        self.PeopleCollaborator = None
        self.PeopleColumnist = None
        self.PeopleComedian = None
        self.PeopleDesigner = None
        self.PeopleDirector = None
        self.PeopleGuest = None
        self.PeopleHost = None
        self.PeopleJournalist = None
        self.PeoplePerformer = None
        self.PeoplePersonCited = None
        self.PeopleSpeaker = None
        self.PeopleWriter = None
        self.PromoDescription = None
        self.PromoTitle = None
        self.Rating = None
        self.RelatedURL1 = None
        self.RelatedURL2 = None
        self.RelatedURL3 = None
        self.RelatedURL4 = None
        self.RelatedURL5 = None
        self.RelatedURLText1 = None
        self.RelatedURLText2 = None
        self.RelatedURLText3 = None
        self.RelatedURLText4 = None
        self.RelatedURLText5 = None
        self.RelatedURLimage1 = None
        self.RelatedURLimage2 = None
        self.RelatedURLimage3 = None
        self.RelatedURLimage4 = None
        self.RelatedURLimage5 = None
        self.SeasonAndEpisode = None
        self.SeasonAndEpisodeLong = None
        self.SeasonNumber = None
        self.Show = None
        self.ShowSearch = None
        self.ShowSeasonSearch = None
        self.StatusMedia = None
        self.Subtitle = None
        self.Team1CountryCode = None
        self.Team2CountryCode = None
        self.Title = None
        self.TitleID = None
        self.TitleSearch = None
        self.Url = None
        self.UrlEmission = None
        self.Year = None
        self.iTunesLinkUrl = None

    def get_title(self):
        return self.Title

    def get_id(self):
        return self.Id

    def get_year(self):
        return self.Year

    def get_genre_title(self):
        return self.GenreTitle

    def get_url(self):
        return self.Url

    def get_season_number(self):
        return self.SeasonNumber

    def get_episode_number(self):
        return self.EpisodeNumber

    def get_sae(self):
        return self.SeasonAndEpisode

    def get_description(self):
        return self.Description

    def get_emission_id(self):
        return self.CategoryId

    def get_air_date(self):
        if self.AirDateFormated is None:
            return None

        dt = datetime.datetime.strptime(self.AirDateFormated, '%Y%m%d')

        return dt.date()

    def set_emission(self, emission):
        self._emission = emission

    def get_emission(self):
        return self._emission

    @staticmethod
    def _get_video_bitrates(playlist):
        bitrates = []

        for stream in playlist.streams:
            index = os.path.basename(stream.uri)

            # TOU.TV team doesnt use the "AUDIO" or "VIDEO" M3U8 tag so we must
            # parse the URL to find out about video stream:
            #   index_X_av.m3u8 -> audio-video (av)
            #   index_X_a.m3u8 -> audio (a)
            if index.split('_', 2)[2][0:2] == 'av':
                bitrates.append(stream.bandwidth)

        return bitrates

    def get_available_bitrates(self):
        # Get playlist
        playlist = toutv.dl.Downloader.get_episode_playlist(self)

        # Get video bitrates
        bitrates = Episode._get_video_bitrates(playlist)

        return sorted(bitrates)

    def __str__(self):
        return '{} ({})'.format(self.get_title(), self.get_id())


class EmissionRepertoire(AbstractEmission):
    def __init__(self):
        self.AnneeProduction = None
        self.CategorieDuree = None
        self.DateArrivee = None
        self.DateDepart = None
        self.DateRetraitOuEmbargo = None
        self.DescriptionUnavailableText = None
        self.DescriptionUpcomingText = None
        self.Genre = None
        self.Id = None
        self.ImagePromoNormalK = None
        self.IsGeolocalise = None
        self.NombreEpisodes = None
        self.NombreSaisons = None
        self.ParentId = None
        self.Pays = None
        self.SaisonsDisponibles = None
        self.Titre = None
        self.TitreIndex = None
        self.Url = None

    def get_title(self):
        return self.Titre

    def get_country(self):
        return self.Pays

    def get_year(self):
        return self.AnneeProduction

class SearchResults:
    def __init__(self):
        self.ModifiedQuery = None
        self.Results = None

    def get_modified_query(self):
        return self.ModifiedQuery

    def get_results(self):
        return self.Results

class SearchResultData:
    def __init__(self):
        self.Emission = None
        self.Episode = None

    def get_emission(self):
        return self.Emission

    def get_episode(self):
        return self.Episode

class Repertoire:
    def __init__(self):
        self.Emissions = None
        self.Genres = None
        self.Pays = None

    def get_emissions(self):
        return self.Emissions
