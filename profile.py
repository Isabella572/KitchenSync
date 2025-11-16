from profile_utils import *
import random
from entities import user

st.title("Active Profiles")

profile_expander(True)

def display_profile(profile: User):
    st.write(f"Name: {profile.name}".title())
    requirements = profile.requirements.requirements_vector
    if not any(requirements):
        st.write("No dietary requirements")
    else:
        requirement_indices = [i for i, val in enumerate(requirements) if val]
        requirements_human_readable = [
            profile.requirements.requirement_from_index[i] for i in requirement_indices
            ]
        st.write(f"Dietary requirements: {requirements_human_readable}")
    

for profile in get_all_profiles():
    display_profile(profile)
    profile_expander(False, profile.name)
