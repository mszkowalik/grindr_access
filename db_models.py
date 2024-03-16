from mongoengine import StringField, IntField, ListField, DictField, BooleanField, FloatField, Document

class baseProfileModel(Document):
    meta = {
        'abstract': True,
    }
    profileId = IntField(required=True)
    created = IntField()
    updated = IntField()
    last_lat = FloatField()
    last_lon = FloatField()
    last_gh = StringField()
    last_batch_timestamp = IntField()
    cover_photo = StringField()
    profileType = StringField()

    lastOnline = IntField()
    photoMediaHashes = ListField(StringField())
    heightCm = IntField()
    weightGrams = IntField()
    lookingFor = ListField(IntField())
    tribes = ListField(IntField())
    meetAt = ListField(IntField())
    vaccines = ListField(IntField())
    genders = ListField(IntField())
    pronouns = ListField(IntField())
    bodyType = IntField()
    approximateDistance = BooleanField()
    tags = ListField(StringField())
    isFavorite = BooleanField()
    socialNetworks = ListField(DictField())
    isBoosting = BooleanField()
    hasChattedInLast24Hrs = BooleanField()
    hasUnviewedSpark = BooleanField()
    isTeleporting = BooleanField()
    isRightNow = BooleanField()
    unreadCount = IntField()
    rightNow = StringField()
    distanceMeters = IntField()
    relationshipStatus = IntField()
    aboutMe = StringField()
    age = IntField()
    ethnicity = IntField()
    sexualPosition = IntField()
    acceptsNsfwPics = IntField()
    hivStatus = IntField()
    displayName = StringField()
    lastTestedDate = IntField()

class profileModel(baseProfileModel):
    meta = {
        'collection': 'profiles',
        'indexes': [
            {
                'fields': ['profileId'],
                'unique': True,
            },
        ]
    }

class aggregatedProfileModel(baseProfileModel):
    meta = {
            'collection': 'aggregated_profiles',
            'indexes': [
                {
                    'fields': ['profileId'],
                    'unique': True,
                },
            ]
        }

class scrapedProfileModel(Document):
    meta = {
        'collection': 'scraped_profiles',
        'indexes': [
            {
                'fields': ['batch_timestamp','anchor_gh','profileId'],
                'unique': True,
            },
        ],
    }
    profileId = IntField(required=True)
    batch_timestamp = IntField(required=True)
    created = IntField()
    anchor_gh = StringField(required=True)
    anchor_lat = FloatField()
    anchor_lon = FloatField()
    distance_from_anchor = IntField()

class profileHistoryModel(Document):
    meta = {
        'collection': 'profile_history',
        'indexes': [
            {
                'fields': ['timestamp','profileId'],
                'unique': True,
            },
        ],
    }
    profileId = IntField(required=True)
    timestamp = IntField(required=True)
    diff = DictField()

class profileLocationModel(Document):
    meta = {
        'collection': 'profile_locations',
        'indexes': [
            {
                'fields': ['timestamp','profileId'],
                'unique': True,
            },
        ],
    }
    profileId = IntField(required=True)
    timestamp = IntField(required=True)
    lat = FloatField()
    lon = FloatField()
    batch_timestamp = IntField()
    geoHash = StringField()