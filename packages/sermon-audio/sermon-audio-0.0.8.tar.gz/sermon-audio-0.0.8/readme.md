# Sermon Audio API

Sermon Audio API is a python wrapper for the APIs of ([http://www.sermonaudio.com/api](http://www.sermonaudio.com/api))

## Install

1. pip install sermon-audio

## Usage

#### Get Speakers By Member Id

	from sermonaudio import SermonAudioAPI
	
	speakers = SermonAudioAPI.get_speakers_by_member_id(member_id='communitybapt')

	print speakers

#### Get Sermon List

	from sermonaudio import SermonAudioAPI

	api = SermonAudioAPI('username', 'password')
	
	# There are only a few categories you can search for:
	#     speaker
	#     eventtype
	#     series
	#     year
	
	sermons = api.get_sermon_list(category='year', search_term='2013')
	
	print sermons

#### Get Sermon Info

	from sermonaudio import SermonAudioAPI
	
	api = SermonAudioAPI('username', 'password')
	
	sermon = api.get_sermon_info(sermon_id='328131022290')
	
	print sermon
	
#### Newest Sermons By Speaker

	from sermonaudio import SermonAudioAPI 
	
	sermons = SermonAudioAPI.newest_sermons_by_speaker(speaker='David Whitcomb')
	
	print sermons
	
#### Newest Sermons By Member Id

	from sermonaudio import SermonAudioAPI
	
	sermons = SermonAudioAPI.newest_sermons_by_member_id(member_id='communitybapt')
	
	print sermons
	
#### Get Event Types

	from sermonaudio import SermonAudioAPI
	
	event_types = SermonAudioAPI.get_event_types()
	
	print event_types
	
#### Get Languages

	from sermonaudio import SermonAudioAPI
	
	languages = SermonAudioAPI.get_languages()
	
	print languages
	
#### Get Newest Series By Member Id

	from sermonaudio import SermonAudioAPI

	series = SermonAudioAPI.get_newest_series_by_member_id(member_id='communitybapt')
	
	print series
	
#### Get Series By Member Id

	from sermonaudio import SermonAudioAPI
	
	series = SermonAudioAPI.get_series_by_member_id(member_id='communitybapt')

	print series
	
#### Get Speakers By Keyword

	from sermonaudio import SermonAudioAPI
	
	speakers = SermonAudioAPI.get_speakers_by_keyword(keyword='love')
