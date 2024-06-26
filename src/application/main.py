print('Welcome to the Transport Calculator!')
print('====================================')

perLitrePetrolCost = 2.7

perLitrePetrolCost = input('\nHow much are you paying per litre of petrol right now? ')

perKmTransportCost = 0.2348

numberOfSavedLocations = 0
totalWeeklyTransportCosts = 0

petrolMileageForYourCar = 14 #The distance travelled per litre of petrol by the individual's car (set to default at the start)

petrolMileageForYourCar = input('\nWhat is your car\'s petrol mileage (how many kms it travels per litre)? ')

moreLocationsToAdd = False

print('You have ' + str(numberOfSavedLocations) + ' locations saved currently.')

moreLocationsToAddAnswer = input('\nWould you like to add more locations that you visit? Answer \'Y\' for yes otherwise no more locations will be added. ')
if moreLocationsToAddAnswer == 'Y':
    moreLocationsToAdd = True
else:
    moreLocationsToAdd = False

while moreLocationsToAdd:

    print('\n-----------Adding new location----------------')
    locationName = input('What is the name of this location? ')
    locationDistanceFromHome = int(input('How far (in kms) do you have to travel for this location (one-way)? '))
    travellingFrequency = int(input('How often do you travel to this location weekly? '))
    travelByCarAnswer = input('Do you travel here by car? Answer \'Y\' for yes otherwise it will be assumed you travel here using public transport. ')
    travelByCar = False
    if travelByCarAnswer == 'Y':
        travelByCar = True
    else:
        travelByCar = False

    weeklyDistanceToTravelToThisLocation = locationDistanceFromHome * 2 * travellingFrequency

    weeklyCostToTravelToThisLocation = 0

    if (travelByCar):
        weeklyCostToTravelToThisLocation += weeklyDistanceToTravelToThisLocation/int(petrolMileageForYourCar) * float(perLitrePetrolCost)
    else:
        weeklyCostToTravelToThisLocation += weeklyDistanceToTravelToThisLocation * perKmTransportCost

    numberOfSavedLocations += 1

    totalWeeklyTransportCosts += weeklyCostToTravelToThisLocation

    print('\nYour weekly transportation costs are: ' + str(totalWeeklyTransportCosts) + '.')

    totalAnnualTransportCosts = totalWeeklyTransportCosts * 52
    print('Your annual transportation costs are: ' + str(totalAnnualTransportCosts) + '.')

    moreLocationsToAddAnswer = input('\nYou have ' + str(numberOfSavedLocations) + ' locations saved currently. Would you like to add more locations that you visit? ')
    if moreLocationsToAddAnswer == 'Y':
        moreLocationsToAdd = True
    else:
        moreLocationsToAdd = False

print('\nHope this was helpful!')