from fastapi import FastAPI
from SeleniumDriver import SeleniumDriver
from datetime import datetime

app = FastAPI()
selenium_driver = SeleniumDriver()

@app.get("/")
def root():
    return {"message": "Welcome to Schedule Service API!"}

@app.get("/schedule/services")
def get_services():
    services = selenium_driver.fetch_select_options("firstSelectControl")
    
    return services

@app.get("/schedule/locations")
def get_locations(service):
    locations = selenium_driver.fetch_select_options("secondSelectControl", service=service)    
    
    return locations

@app.get("/schedule/dates")
def get_dates(service, location):
    fm_date_cells, lm_date_cells, dates = selenium_driver.get_available_dates("dateControl", service, location)
    
    return dates

@app.get("/schedule/hours")
def get_hours(service, location, date:datetime):
    
    time = selenium_driver.fetch_select_options("timeControl", service=service, location=location, date=date)

    return time

@app.on_event("shutdown")
def shutdown_event():
    selenium_driver.close()

