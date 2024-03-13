import random
import os
from time import sleep
from datetime import datetime
from copy import deepcopy
from dotenv import load_dotenv
from mongoengine import connect, NotUniqueError

load_dotenv()

from grindr_access.grindrUser import grindrUser
from profile_model import ScrapedProfileModel, ProfileModel
from stalkr import generate_grid_points, localizeProfile


mail = os.getenv('GRINDR_MAIL')
password = os.getenv('GRINDR_PASS')
krk_lat = float(os.getenv('LOC_LAT'))
krk_lon = float(os.getenv('LOC_LON'))

while True:
    user = grindrUser()
    user.login(mail, password)
    connect(
        db=os.getenv('MONGO_DB'),
        host=os.getenv('MONGO_URL'),
        port=int(os.getenv('MONGO_PORT')),
        username=os.getenv('MONGO_USR'),
        password=os.getenv('MONGO_PWD'),
        authentication_source="admin"
        )

    # Example usage
    center_lat, center_lon = krk_lat, krk_lon # Equator and Prime Meridian
    side_m = 10000 # 10 km side length
    accuracy_m = 1000 # 1000m
    points_per_side = int(side_m/accuracy_m) # Generate 100 points

    grid_points = generate_grid_points(center_lat, center_lon, side_m, points_per_side,jitter_m=200)

    i = 0
    scraped_profiles = {}
    batch_timestamp = int(datetime.now().timestamp() * 1000)
    print("###############################################")
    print(f"Scraping {len(grid_points)} points")

    for point in grid_points:
        timestamp = int(datetime.now().timestamp() * 1000)
        time_to_sleep = random.uniform(0, 1)
        print(f"{i}/{len(grid_points)} - {point[0]}\t{point[1]}\t - {timestamp} - {time_to_sleep}")
        profile_list = user.getProfiles(point[0], point[1])
        for response in profile_list['items']:
            response_profile = response['data']
            prof = {}
            prof.update(response_profile)
            # Filter out upsell banners or other non-profiles
            profile_types = ["PartialProfileV1", "FullProfileV1"]
            if any(element in response_profile.get('@type') for element in profile_types):
                #fill all the fields obtained from request
                prof['profileId'] = response_profile['profileId']
                prof['created'] = timestamp
                prof['lat'] =  point[0] # Add the lat and lon of the anchor point
                prof['lon'] =  point[1]
                prof['batch_timestamp'] = batch_timestamp
                # Save the profile to the database
                scraped_prof = ScrapedProfileModel(**prof)
                scraped_prof.save()
                # if the profile is not in the dict, add it
                if scraped_profiles.get(scraped_prof.profileId) is None:
                    scraped_profiles[scraped_prof.profileId] = []
                scraped_profiles[scraped_prof.profileId].append(deepcopy(prof))
        # Sleep for a random amount of time to avoid being rate limited
        sleep(time_to_sleep)
        i+=1


    print("###############################################")
    print("Localizing profiles...")
    #multilateration results, localized profiles. profileId is the key
    ml_results = {}
    # dict with localized profiles (LocationHistoryModel) . profileId is the key
    localized_profiles = {}
    # iterate over all profiles and localize them
    for profileId, scraped_profileList in scraped_profiles.items():
        print(f"Localizing profile {profileId}...")
        new_locations, loc_profile = localizeProfile(scraped_profileList)
        if loc_profile:
            localized_profiles[profileId] = loc_profile
            try:
                loc_profile.save()  # Attempt to save the new LocationHistoryModel profile
            except NotUniqueError:
                print("A document with the same unique index already exists. Ignoring.")
        ml_results.update(new_locations)

    print("###############################################")
    print("Updating profiles...")
    #once localized, update the profiles, and download images
    for profileId, scraped_profileList in scraped_profiles.items():
        print(f"Updating profile {profileId}...")
        profile = ProfileModel.objects(profileId=profileId).first() # type: ignore
        #prepare data for update:
        profile_data = {}
        for prof in scraped_profileList:
            profile_data.update(prof)
        #id profile doesnt exist, create it
        if profile is None:
            print(f"Profile {profileId} not found in the database")
            profile = ProfileModel(**profile_data)
            profile.save()

        #update the profile
        old_profile_data:dict = profile.to_mongo().to_dict()
        old_profile_data.update(profile_data)
        if profile.profileId in localized_profiles.keys():
            localization_data:dict = localized_profiles[profileId].to_mongo().to_dict()
            old_profile_data.update(localization_data)
        del old_profile_data['_id']

        profile.update(**old_profile_data)

        #download images
        for image_hash in profile.photoMediaHashes:
            if not image_hash in profile.images.keys():
                print(f"Downloading image {image_hash}")
                image = user.getImage(image_hash)
                image_str = user.toBase64(image)
                profile.images[image_hash] = image_str
        #set cover photo
        if len(profile.photoMediaHashes) > 0:
            profile.cover_photo = profile.images[profile.photoMediaHashes[0]]
        else:
            profile.cover_photo = ""
        profile.save()
    print("###############################################")
    print(f"Scraped {len(scraped_profiles)} profiles")
    loopinterval = 20*60 + random.uniform(-5*60, 5*60)
    print(f"Sleeping for {loopinterval} seconds")
    sleep(loopinterval)