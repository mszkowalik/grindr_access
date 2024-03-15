import os
from dotenv import load_dotenv
from datetime import datetime
from copy import deepcopy
from mongoengine import connect, NotUniqueError
from pymongo import errors
import pygeohash as gh
from deepdiff import DeepDiff
from stalkr import generate_grid_points, localizeProfile
from grindr_access.grindr_user import GrindrUser
from time import sleep
from db_models import scrapedProfileModel, profileModel, profileHistoryModel, aggregatedProfileModel

load_dotenv()

connect(
    # db=os.getenv('MONGO_DB'),
    db="grindr",
    host=os.getenv('MONGO_URL'),
    port=27017,
    username=os.getenv('MONGO_USR'),
    password=os.getenv('MONGO_PWD'),
    authentication_source="admin"
    )
user = GrindrUser()
mail = os.getenv('GRINDR_MAIL')
password = os.getenv('GRINDR_PASS')
krk_lat = 50.059185
krk_lon = 19.937809

while True:
    print("Logging in...")
    user.login(mail, password)

    center_lat, center_lon = krk_lat, krk_lon # Equator and Prime Meridian
    side_m = 10000 # 10 km side length
    accuracy_m = 1000 # 1000m
    points_per_side = int(side_m/accuracy_m) # Generate 100 points

    grid_points = generate_grid_points(center_lat, center_lon, side_m, points_per_side,jitter_m=200)

    scraped_profiles = {}
    localization_data = {}
    batch_timestamp = int(datetime.now().timestamp() * 1000)

    i=0
    for anchor_point in grid_points:
        created = int(datetime.now().timestamp() * 1000)
        anchor_gh = gh.encode(anchor_point[0], anchor_point[1],12)
        actual_anchor_point = list(gh.decode(anchor_gh))
        # Get the profiles for the current point from grindr API
        profile_list = user.getProfiles(actual_anchor_point[0], actual_anchor_point[1])
        print(f"{i}/{len(grid_points)}\t Anchor_point: {actual_anchor_point}\t Anchor_gh: {anchor_gh}")
        for response in profile_list['items']:
            response_profile = response['data']
            prof = {}
            # Filter out upsell banners or other non-profiles
            profile_types = ["PartialProfileV1", "FullProfileV1"]
            is_profile = any(element in response_profile.get('@type') for element in profile_types)
            has_distance = response_profile.get('distanceMeters') is not None
            if is_profile and has_distance:
                #fill all the fields obtained from request
                prof['profileId'] = response_profile['profileId']
                prof['created'] = created
                prof['anchor_lat'] =  actual_anchor_point[0] # Add the lat and lon of the anchor point
                prof['anchor_lon'] =  actual_anchor_point[1]
                prof['anchor_gh'] = anchor_gh
                prof['batch_timestamp'] = batch_timestamp
                prof['distance_from_anchor'] = response_profile['distanceMeters']
                # Save the profile to the database
                scraped_prof = scrapedProfileModel(**prof)
                scraped_prof.save()
                # store locally for further processing
                if scraped_profiles.get(scraped_prof.profileId) is None:
                    scraped_profiles[scraped_prof.profileId] = []
                    localization_data[scraped_prof.profileId] = []

                #rename the profileType field to avoid conflicts with mongoengine
                if response_profile.get('@type'):
                    response_profile['profileType'] =  response_profile.pop('@type')
                keys_to_remove = ['upsellItemType', 'distanceMeters']
                for key in keys_to_remove:
                    response_profile.pop(key, None)

                scraped_profiles[scraped_prof.profileId].append(deepcopy(response_profile))
                localization_data[scraped_prof.profileId].append(prof)
        i+=1

    for profileId, profiles in scraped_profiles.items():
        # iterate over all profiles and merge all the data by updating te output dict
        merged_profile_dict = profileModel().to_mongo().to_dict()

        for profile_dict in profiles:
            merged_profile_dict.update(profile_dict)

        profile = profileModel.objects(profileId=profileId).first()
        aggregated_profile = aggregatedProfileModel.objects(profileId=profileId).first()
        # if profile does not exist, create it
        if not profile:
            merged_profile_dict['created'] = batch_timestamp
            merged_profile_dict['updated'] = batch_timestamp
            profile = profileModel(**merged_profile_dict)
            profile.save()

        if not aggregated_profile:
            aggregated_profile = aggregatedProfileModel(**merged_profile_dict)
            if len(aggregated_profile.photoMediaHashes) > 0:
                # user.get_image(aggregated_profile.photoMediaHashes[0])
                pass
            aggregated_profile.save()

        current_profile_dict =  {}
        if profile:
            current_profile_dict = profile.to_mongo().to_dict()
        # those fielsd are not received from the API, so we need to remove them from the current profile
        keys_to_remove = ['_id','created', 'updated', 'last_lat', 'last_lon', 'cover_photo']

        for key in keys_to_remove:
            current_profile_dict.pop(key, None)

        # compare the current profile with the merged one
        diff = DeepDiff(current_profile_dict, merged_profile_dict, ignore_order=True, verbose_level=2).to_dict()
        # if there is a difference, update the profile
        if diff != {}:
            print("Profile has changed: ", profileId)
            print(diff)
            profileHistory = profileHistoryModel(profileId=profileId, timestamp=batch_timestamp, diff=diff)
            try:
                profileHistory.save()
            except (NotUniqueError, errors.DuplicateKeyError):
                    print("A document with the same unique index already exists. Ignoring.")

            # update the profile
            merged_profile_dict['updated'] = batch_timestamp
            profile.update(**merged_profile_dict)
            #aggregate the profile history
            new_dict = deepcopy(current_profile_dict)
            new_dict.update(merged_profile_dict)
            new_dict['updated'] = batch_timestamp
            aggregated_profile.update(**new_dict)

    #multilateration results, localized profiles. profileId is the key
    ml_results = {}
    # dict with localized profiles (LocationHistoryModel) . profileId is the key
    localized_profiles = {}
    # iterate over all profiles and localize them
    for profileId, scraped_profileList in localization_data.items():
        print(f"Localizing profile {profileId}...")
        new_locations, loc_profile = localizeProfile(scraped_profileList, max_distance=1.5*accuracy_m)
        if loc_profile:
            localized_profiles[profileId] = loc_profile
            try:
                loc_profile.save()  # Attempt to save the new LocationHistoryModel profile
            except NotUniqueError:
                print("A document with the same unique index already exists. Ignoring.")
        ml_results.update(new_locations)
    timeout = 5*60
    print("Localized profiles: ", len(localized_profiles))
    print(f"sleeping for {timeout/60} minutes...")
    sleep(timeout)
