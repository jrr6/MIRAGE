import math

# https://github.com/neilbartlett/color-temperature/blob/master/index.js
def colorTemperature2rgb(kelvin):
    temperature = kelvin / 100.0
    if (temperature < 66.0):
        red = 255
    else:
        red = temperature - 55.0;
        red = 351.97690566805693+ 0.114206453784165 * red - 40.25366309332127 * math.log(red);
        if (red < 0): red = 0
        if (red > 255): red = 255

    if (temperature < 66.0):
        green = temperature - 2
        green = -155.25485562709179 - 0.44596950469579133 * green + 104.49216199393888 * math.log(green)
        if (green < 0): green = 0;
        if (green > 255): green = 255
    else:
        green = temperature - 50.0
        green = 325.4494125711974 + 0.07943456536662342 * green - 28.0852963507957 * math.log(green)
        if (green < 0): green = 0
        if (green > 255): green = 255

    if (temperature >= 66.0):
        blue = 255
    else:
        if (temperature <= 20.0):
          blue = 0
        else:
          blue = temperature - 10
          blue = -254.76935184120902 + 0.8274096064007395 * blue + 115.67994401066147 * math.log(blue)
          if (blue < 0): blue = 0
          if (blue > 255): blue = 255

    return {'red': round(red), 'blue': round(blue), 'green': round(green)}

def rgb2colorTemperature(red, green, blue):
    epsilon=0.4
    minTemperature = 1000
    maxTemperature = 40000
    while maxTemperature - minTemperature > epsilon:
        temperature = (maxTemperature + minTemperature) / 2
        testRGB = colorTemperature2rgb(temperature)
        # FIXME: this crashes
        if ((testRGB['blue'] / testRGB['red']) >= (blue / red)):
            maxTemperature = temperature
        else:
            minTemperature = temperature
    return round(temperature)