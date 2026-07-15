import streamlit as st
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from streamlit_gsheets import GSheetsConnection

# Creating pre-defined Sapling list
SaplingList = ["Sehtoot", "Kathal", "Lemon", "Guava",
               "Malta fruit(sweet orange)", "Rudraksh",
               "Bael", "Fig", "Molsari", "Arjun", "Chukrassia",
               "Ashok Pendula", "Badi Sawani", "Neem", "Mahua",
               "Kachnar", "Neeli Gulmohar", "Aam (Ramkela)",
               "Jamun", "Papri", "Palash", "Amaltash",
               "Cassia siama", "Amla", "Gulmohar (Pink)", "Pilkhan",
               "Silver Oak", "Kadam", "Raat ki Rani", "Champa",
               "Mogra", "Imli", "Bougainvillea", "Peepal", "Bargad"]

# GPS Extraction Functions
def getDecimalFromDms(dms, ref):
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0
    if ref in ["S", "W"]:
        return -1 * (degrees + minutes + seconds)
    return degrees + minutes + seconds

def extractExifGps(imageFile):
    try:
        image = image.open(imageFile)
        exifData = image.getExif()
        if not exifData:
            return None, None, None
        
        gpsInfo = {}
        dateTaken = "N/A"

        for tagId, value in exifData.items():
            tag = TAGS.get(tagId, tagId)
            if tag == "DateTimeOriginal" or tag == "DateTime":
                dateTaken = value
            if tag == "GPSInfo":
                for t in value:
                    subTag = GPSTAGS.get(t, t)
                    gpsInfo[subTag] = value[t]

        if "GPSLatitude" in gpsInfo and "GPSLongitude" in gpsInfo:
            latitude = getDecimalFromDms(gpsInfo["GPSLatitude"], gpsInfo.get("GPSLatitudeRef", "N"))
            longitude = getDecimalFromDms(gpsInfo["GPSLongitude"], gpsInfo.get("GPSLongitudeRef", "E"))
            return latitude, longitude, dateTaken
        
        return None, None, dateTaken
    except Exception as e:
        st.error(f"Error parsing image: {e}")
        return None, None, None
    
# streamLit UI
st.set_page_config(page_title="Live Sapling Tracker", layout="centered")
st.title("🌱 Live Sapling Geotag Integrator")
st.write("Upload processed photos to instantly log them into the central organizational spreadsheet.")

# Establishing connection to Google Sheets
# (Requires setting up secrets in your streamLit dashboard later)
connection = st.connection("gsheets", type=GSheetsConnection)

# Form Element
selectedSaplings = st.selectbox("Select Sapling Species:", SaplingList)
saplingType = st.radio("Sapling Type: ", ["Flowering", "Fruit Bearing", "Shade Giving", "Medicinal"])
uploadedFile = st.file_uploader("Upload Image File", type=["jpg", "jpeg"])

if uploadedFile is not None:
    st.image(uploadedFile, caption="Target Image", width=250)
    
    if st.button("🚀 Integrate into Master Sheet"):
        latitude, longitude, dateTaken = extractExifGps(uploadedFile)

        if latitude and longitude:
            # it will fetch the existing data from the cloud sheet
            existingData = connection.read()

            # Creates the new row dictionary
            newData = {
                "Species Name": [selectedSaplings],
                "Type": [saplingType],
                "Latitude": [latitude],
                "Longitude": [longitude],
                "Timestamp": [dateTaken]
            }
            newDF = pd.DataFrame(newData)

            # Append and Update the cloud sheet
            updatedDF = pd.concat([existingData, newDF], ignore_index=True)
            connection.update(data=updatedDF)

            st.success("✅ Data successfully injected into the central excel sheet! 🤗👍🏻")
        else:
            st.error("Missing geotag coordinates in this photo. Kindly ensure location metadata is active. 😅")

# Providing the public view link on screen for transparency
st.markdown("---")
st.info("🔗 Public Spreadsheet Link:- Anyone with this link 👇🏻 can view the live database dashboard.")

st.write("`https://docs.google.com/spreadsheets/d/1m7o8hUwJAiIbZNFM6U-WsEStdtItynbGauwM5VNsSzs/edit?usp=sharing`")