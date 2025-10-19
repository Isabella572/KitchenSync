from profile_utils import *
import random

st.title("Active Profiles")

profile_expander(True)

for profile in get_all_profiles():
    st.write(profile)
    if st.button("Edit profile", key=profile[1] + str(random.randint(0,99999))):
        profile_expander(False, profile[1])
