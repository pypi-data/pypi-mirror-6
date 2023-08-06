# Sermon Audio API

Sermon Audio API is a python wrapper for the APIs of ([http://www.sermonaudio.com/api](http://www.sermonaudio.com/api))

## Install

1. pip install sermon-audio

## Usage

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

	import SermonAudioAPI
	
	api = SermonAudioAPI('username', 'password')
	
	sermon = api.get_sermon_info(sermon_id='328131022290')
	
	print sermon
	
#### Newest Sermons By Speaker

	import SermonAudioAPI 
	
	sermons = SermonAudioAPI.newest_sermons_by_speaker(speaker='David Whitcomb')
	
	print sermons
	
#### Newest Sermons By Member Id

	import SermonAudioAPI
	
	sermons = SermonAudioAPI.newest_sermons_by_member_id(member_id='communitybapt')
	
	print sermons
	
#### Get Event Types

	import SermonAudioAPI
	
	event_types = SermonAudioAPI.get_event_types()
	
	print event_types
	
#### Get Languages

	import SermonAudioAPI
	
	languages = SermonAudioAPI.get_languages()
	
	print languages
	
#### Get Newest Series By Member Id

	import SermonAudioAPI

	series = SermonAudioAPI.get_newest_series_by_member_id(member_id='communitybapt')
	
	print series
	
#### Get Series By Member Id

	import SermonAudioAPI
	
	series = SermonAudioAPI.get_series_by_member_id(member_id='communitybapt')

	print series
	
#### Get Speakers By Member Id

	import SermonAudioAPI
	
	speakers = SermonAudioAPI.get_speakers_by_member_id(member_id='communitybapt')

	print speakers
	
#### Get Speakers By Keyword

	import SermonAudioAPI
	
	speakers = SermonAudioAPI.get_speakers_by_keyword(keyword='love')