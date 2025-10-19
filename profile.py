from profile_utils import *

st.title("Active Profiles")

profile_expander(True)

for profile in get_all_profiles():
    st.write(profile)
    if st.button("Edit profile"):
        profile_expander(False)
