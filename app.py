from shiny import App, render, ui
import pandas

data = pandas.read_csv("data.csv")
data["Solar"]=data["Solar"].apply(pandas.to_numeric)
data["Wind Offshore"]=data["Wind Offshore"].apply(pandas.to_numeric)
data["Wind Onshore"]=data["Wind Onshore"].apply(pandas.to_numeric)
data["Last"]=data["Last"].apply(pandas.to_numeric)
slast = data["Last"].sum()
total = data["Solar"].sum()+data["Wind Offshore"].sum()+data["Wind Onshore"].sum()
average = total/data.shape[0]
data["Last"]=data["Last"]*total/slast
laverage = data["Last"].sum()/data.shape[0]


data["Generation"]=data["Solar"]+data["Wind Offshore"]+data["Wind Onshore"]

# Sanity Check für Daten
print(data.keys())
print(data.columns.to_list())

print ( total )
print ( average )
print ( laverage )
print ( data["Generation"].sum() )
print ( data["Last"].sum() )

app_ui = ui.page_fluid(
    ui.h2("Hello Shiny!"),
    ui.input_slider("margin", "% Überproduktion", min = 100, max = 200, value = 100, step = 1),
    ui.input_slider("n", "% Speicher der Gesamterzeugung", min = 0, max = 10, value = 0, step = 0.1),
    ui.input_slider("init", "% Speicherfüllstand am Start", min = 0, max = 100, value = 0, step = 1),
    ui.input_numeric("demand","Benötigte Energie in TWh",2407),
    ui.input_numeric("storagecost","Speicher Kosten €/kWh",90),
    ui.output_text_verbatim("txt"),
)


def server(input, output, session):
    @output
    @render.text
    def txt():
        data.reset_index()
        maxstored = input.n()*total/100
        stored = input.init()*maxstored/100
        missed = 0
        wasted = 0
        for index, row in data.iterrows():
            diff = row["Last"]-row["Generation"]*input.margin()/100
            # Mehr Verbrauchen als Generieren
            if ( diff>0 ):
                stored = stored - diff/0.8
                if ( stored < 0 ):
                    missed = missed - stored*0.8
                    stored = 0
            # Weniger Verbrauchen als Generieren
            else:
                stored = stored - diff*0.8
                if ( stored>maxstored ):
                    wasted = wasted + (stored-maxstored)/0.8
                    stored = maxstored

        costtotal = input.demand()*10e9*input.storagecost()*input.n()/100
        return f"UngenutzteEnergie %: {100*wasted/total} Fehlende Energie %: {100*missed/total} Speicherstand Ende %: {100*stored/maxstored} Speicherkosten in Milliarden €: {costtotal/10e9}"


app = App(app_ui, server)