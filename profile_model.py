from mongoengine import DynamicDocument, StringField, IntField, ListField, DictField, BooleanField, FloatField
# Define a Document class for your "scraped_data" collection
class ProfileModel(DynamicDocument):
    meta = {
        'collection': 'profiles',
        'indexes': [
            {
                'fields': ['profileId'],
                'unique': True,
            },
        ],
    }
    profileId = IntField(required=True)
    created = IntField()
    lat = FloatField()
    lon = FloatField()
    batch_timestamp = IntField(required=True)
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

    history = DictField(DictField())

class ScrapedProfileModel(DynamicDocument):
    meta = {'collection': 'scraped_data'}
    profileId = IntField(required=True)
    created = IntField()
    lat = FloatField()
    lon = FloatField()
    batch_timestamp = IntField()
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
    # cascadePlacementName

class LocatedProfileModel(DynamicDocument):
    meta = {
        'collection': 'localizations',
        'indexes': [
            {
                'fields': ['profileId', 'batch_timestamp'],
                'unique': True,
            },
        ],
    }
    profileId = IntField(required=True)
    created = IntField()
    lat = FloatField()
    lon = FloatField()
    batch_timestamp = IntField(required=True)
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
    # cascadePlacementName