print('Welcome to the Transport Calculator!')
print('====================================')

perLitrePetrolCost = 2.7
perKmTransportCost = 0.2348

numberOfSavedLocations = 0
totalWeeklyTransportCosts = 0

petrolMileageForYourCar = 14 #The distance travelled per litre of petrol by the individual's car

moreLocationsToAdd = False

moreLocationsToAddAnswer = input('You have ' + str(numberOfSavedLocations) + ' locations saved currently. Would you like to add more locations that you visit?')
if moreLocationsToAddAnswer == 'Y':
    moreLocationsToAdd = True

if (moreLocationsToAdd):
    locationName = input('What is the name of this location? ')
    locationDistanceFromHome = int(input('How far do you have to travel for this location (one-way)? '))
    travellingFrequency = int(input('How often do you travel to this location weekly? '))
    travelByCarAnswer = input('Do you travel here by car? Answer \'Y\' for yes otherwise it will be assumed you travel here using public transport. ')
    travelByCar = False
    if travelByCarAnswer == 'Y':
        travelByCar = True

    weeklyDistanceToTravelToThisLocation = locationDistanceFromHome * 2 * travellingFrequency

    weeklyCostToTravelToThisLocation = 0

    if (travelByCar):
        weeklyCostToTravelToThisLocation += weeklyDistanceToTravelToThisLocation/petrolMileageForYourCar * perLitrePetrolCost
    else:
        weeklyCostToTravelToThisLocation += weeklyDistanceToTravelToThisLocation * perKmTransportCost

    numberOfSavedLocations += 1

    totalWeeklyTransportCosts += weeklyCostToTravelToThisLocation

print('Your weekly transportation costs are: ' + str(totalWeeklyTransportCosts) + '.')

totalAnnualTransportCosts = totalWeeklyTransportCosts * 52
print('Your annual transportation costs are: ' + str(totalAnnualTransportCosts) + '.')
