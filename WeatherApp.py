#import necessary libraries
from tkinter import *
import tkinter as tk
from tkinter import PhotoImage
import requests
from datetime import datetime
from pytz import timezone
from PIL import ImageTk, Image
from time import strftime
from tkinter.ttk import *         
from playsound import playsound
from itertools import count, cycle
import tkintermapview
import time

#create tkinter window
root = tk.Tk()     
root.geometry("1200x650")

# Create Background GIF
class ImageLabel(tk.Label):
    def load(self, im):
        # Check if the image is a file path (string)
        if isinstance(im, str):
            # Open the image using PIL if it's a file path
            im = Image.open(im)
        
        frames = []  # Initialize an empty list to hold the frames of the GIF
        try:
            # Loop through the frames of the GIF
            for i in count(1):
                # Create PhotoImage instances for each frame and append to frames list
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)  # Move to the next frame
        except EOFError:
            pass  # End of frames reached
        
        self.frames = cycle(frames)  # Store the frames in a cycle iterable
        
        try:
            # Get the delay between frames from GIF metadata
            self.delay = im.info['duration']
        except:
            # If metadata doesn't exist, set a default delay of 100 milliseconds
            self.delay = 100
        
        if len(frames) == 1:
            # If only one frame exists, configure the label's image with it
            self.config(image=next(self.frames))
        else:
            # If multiple frames exist, start displaying frames using next_frame()
            self.next_frame()

    def unload(self):
        # Unload the image by setting the label's image to None and clearing stored frames
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            # Update the label's image to the next frame in the cycle
            self.config(image=next(self.frames))
            # Schedule the next frame to display after the specified delay
            self.after(self.delay, self.next_frame)

# Create an instance of ImageLabel and pack it within the root window
lbl = ImageLabel(root)
lbl.pack()
# Load the specified GIF to display as the background of the label
lbl.load('weathergif (1).gif')

#create entry field for user input
textfield = tk.Entry(root, justify="center",width=20,font=("Arial", 25),border="0",fg="black") 
textfield.place(x=100, y=190)
textfield.focus()
#Define the rate limit and the time interval
rate_limit = 10  # Example: 10 requests allowed per minute
time_interval = 60  # Time interval in seconds (1 minute)
#Track the time of the last API request
last_request_time = None

def make_api_request():
    global last_request_time  # Indicate that last_request_time is a global variable
    
    # Check if the last request was made within the time interval to adhere to the rate limit
    if last_request_time is not None and time.time() - last_request_time < time_interval:
        # Calculate the time needed to wait before making the next request
        time_to_wait = time_interval - (time.time() - last_request_time)
        time.sleep(time_to_wait)  # Pause the execution to adhere to the rate limit
    
    # Make the API request
    response = requests.get('https://api.tomorrow.io/v4/timelines')
    
    # Update the last_request_time with the current time to track the latest request time
    last_request_time = time.time()
    
    return response  # Return the API response to the caller

make_api_request()
# Function to format time based on location's timezone
def time_format_for_location(utc_with_tz):
    localy = datetime.utcfromtimestamp(utc_with_tz)
    return localy.time()
# Function to format time based on location's timezone
def Weather():
   # Get the user-input city from the textfield
    Con_City = textfield.get()
    # Create an empty list to store parts of the city string
    place_list = []
    # Split the city string by '/' delimiter and store the parts in place_list
    place_list.extend(Con_City.split("/"))
    # Split the city string by '/' delimiter to obtain individual parts
    parts = Con_City.split("/")
    # Extract the first element from the city string
    first_element = parts[0]
    # Extract the last element (which is presumed to be the city name) from the city string
    city = parts[-1]
    # Create a string 'weather_name' by combining the first element and city with a '/'
    weather_name = first_element + "/" + city
    # Join the last two elements of the city parts separated by a space
    map_string = " ".join(parts[-2:])
    # Reverse the order of words in 'map_string'
    reversed_map_string = " ".join(map_string.split()[::-1])
    # Set the address for a map display, likely using the 'reversed_map_string'
    map.set_address(reversed_map_string, marker=True)
    #Error handling in case city is not entered
    if not city:
        temperature.config(text="Please enter a city")
        return
    #OpenWeather API & URL
    api_key = '53275ef9b001e069d66470b26d0de9da'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    #Tomorrow.io URL
    url2 = "https://api.tomorrow.io/v4/timelines"
    #Tomorrow.io Parameters
    parameters = {
        'location': city,
        'fields': 'temperature',
        'units': 'metric',
        'apikey': 'qSTHWh0XmtXrEVT4uK1AKNPatkkrEqbi',  
        'timesteps': '1d',
        'timezone': 'auto',  
        'endtime': '2023-03-31T00:00:00Z'
    }

    response = requests.get(url2, params=parameters)

    if response.status_code == 200:
        try:
            data = response.json()
            #Extract forecast information and display it
            forecast.delete('1.0', END)  
            results = data['data']['timelines'][0]['intervals']
            for daily_result in results:
                date = daily_result['startTime'][0:10]
                temp = round(daily_result['values']['temperature'])
                forecast.insert(END, f"On {date} it will be {temp} C\n")
        except KeyError as e:
            #Handling changes in forecast data format
            forecast.delete('1.0', END)  
            forecast.insert(END, "Forecast data format has changed. Unable to display forecast.")
            print(f"KeyError: {e}. Forecast data format has changed.")
        except Exception as e:
            #Handling other exceptions during forecast data fetch
            forecast.delete('1.0', END)  
            forecast.insert(END, "Error fetching forecast data.")
            print(f"Error fetching forecast data: {e}")
    else:
        #Handling failed forecast data when fetching
        forecast.delete('1.0', END)  
        forecast.insert(END, "Failed to fetch forecast data.")
        print(f"Failed to fetch forecast data. Status code: {response.status_code}")

    response = requests.get(url)
    if response.status_code != 200:
        temperature.config(text="City not found")
    data = response.json()
    temp = round(data['main']['temp'] -273.15, 2)
    desc = data['weather'][0]['description']
    prsr = data['main']['pressure']
    humid = data['main']['humidity']
    wind = round(data['wind']['speed'] * 3.6, 2)
    rising = data['sys']['sunrise']
    setting = data['sys']['sunset']
    timeSun = data['timezone']
    sunrise_time = time_format_for_location(rising + timeSun)
    sunset_time = time_format_for_location(setting + timeSun)
    cloud = data['clouds']['all']
    mains = data['weather'][0]['main']
    BoldDesc = desc.title()
    try:
        timeZ = timezone(weather_name)
        u_time = datetime.now(timeZ)
        different_time = u_time.strftime("Time is: %d/%m/%y, %I:%M %p")
        diftime.config(text=different_time)
    except Exception as e:
        diftime.config(text="")
    root.after(1000, Weather)
    #Update GUI with information
    temperature.config(text=f"Temperature: {temp}°C")
    pressure.config(text=f"Pressure: {prsr}hPa")
    humidity.config(text=f"Humidity: {humid}%")
    wind_speed.config(text=f"Wind Speed: {wind}m/s")
    cloudy.config(text=f"Clouds: {cloud}%")
    description.config(text=f"Description: {BoldDesc}")
    sunrise.config(text=f"The sun rises at: {sunrise_time}")
    sunset.config(text=f"The sun sets at: {sunset_time}")

def ShowLabel():
    #Function to show information 
    temperature.place(x=100, y=300)
    pressure.place(x=100, y=325)
    humidity.place(x=100, y=350)
    wind_speed.place(x=100, y=375)
    cloudy.place(x=100, y=400)
    description.place(x=100, y=425)
    diftime.place(x=100, y=450)
    sunrise.place(x=100, y=475)
    sunset.place(x=100, y=500)
    forecast.place(x=100, y=525)

#Creating a LabelFrame for the map and placing it in the GUI
map_label = LabelFrame(root)
map_label.place(x=590)
map = tkintermapview.TkinterMapView(map_label, width=600, height=625, corner_radius=0)
map.pack()
#Creating widgets for weather information and setting them to be hidden initially
temperature = tk.Label(root, font=("arial", 15,"bold" ))
temperature.place_forget()
pressure = Label(root, font=("arial", 15,"bold" ))
pressure.place_forget()
humidity = Label(root, font=("arial", 15,"bold" ))
humidity.place_forget()
wind_speed = Label(root, font=("arial", 15,"bold" ))
wind_speed.place_forget()
cloudy = Label(root, font=("arial", 15,"bold" ))
cloudy.place_forget()
description = Label(root, font=("arial", 15,"bold" ))
description.place_forget()
diftime = Label(root, font=("arial", 15, "bold"))
diftime.place_forget()
displaytime = Label(root, font=("arial", 15, "bold"))
displaytime.place(x=85, y=100)
sunrise = Label(root, font=("arial", 15,"bold" ))
sunrise.place_forget()
sunset = Label(root, font=("arial", 15,"bold" ))
sunset.place_forget()
forecast = Text(root, font=("arial", 12), height=10, width=40)
forecast.place_forget
#Creating a search button using an image and setting its properties
searchbutton = PhotoImage(file="blue_search-removebg-preview.png")
searchimage = Button(image=searchbutton,width=10, cursor="hand2", command=lambda: [Weather(), ShowLabel()])                                                                            
searchimage.place(x=60,y=190)
#Function to update the clock label with local time
def clock():
    local_time = strftime("Local time is: %d/%m/%y, %I:%M %p")
    displaytime.config(text=local_time)
    root.after(1000, clock)
#Calling function for clock function to update time continuously
clock()
# Creating a header label for user to know the way to input
header = Label(root,font=("arial", 15, "bold"), text="Enter Continent/Country/City:")
header.place(x=110, y=130)
#Configuring the icon and title
img = PhotoImage(file="Weather2.png")
root.iconphoto(False, img)
root.title("Weather App")
#Starting the Tkiner event loop
root.mainloop()
