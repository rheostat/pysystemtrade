This document is specifically about storing and processsing *futures data*. 

Related documents:

- [Using pysystemtrade as a production trading environment](/docs/production.md)
- [Backtesting with pysystemtrade](/docs/backtesting.md)
- [Connecting pysystemtrade to interactive brokers](/docs/IB.md)

It is broken into three sections. The first, [A futures data workflow](#futures_data_workflow), gives an overview of how data is typically processed. It describes how you would get some data from, store it, and create data suitable for simulation and as an initial state for trading. The next section [Storing futures data](#storing_futures_data) then describes in detail each of the components of the API for storing futures data. In the third and final section [simData objects](#simData_objects) you will see how we hook together individual data components to create a `simData` object that is used by the main simulation system.

Although this document is about futures data, parts two and three are necessary reading if you are trying to create or modify any data objects.


Table of Contents
=================

   * [A futures data workflow](#a-futures-data-workflow)
      * [Setting up some instrument configuration](#setting-up-some-instrument-configuration)
      * [Roll parameter configuration](#roll-parameter-configuration)
      * [Getting historical data for individual futures contracts](#getting-historical-data-for-individual-futures-contracts)
      * [Roll calendars](#roll-calendars)
         * [Approximate roll calendars, adjusted with actual prices](#approximate-roll-calendars-adjusted-with-actual-prices)
            * [Calculate the roll calendar](#calculate-the-roll-calendar)
            * [Checks](#checks)
            * [Write CSV prices](#write-csv-prices)
         * [Roll calendars from existing 'multiple prices' .csv files](#roll-calendars-from-existing-multiple-prices-csv-files)
      * [Creating and storing multiple prices](#creating-and-storing-multiple-prices)
      * [Creating and storing back adjusted prices](#creating-and-storing-back-adjusted-prices)
      * [Backadjusting 'on the fly'](#backadjusting-on-the-fly)
      * [Changing the stitching method](#changing-the-stitching-method)
      * [Getting and storing FX data](#getting-and-storing-fx-data)
   * [Storing and representing futures data](#storing-and-representing-futures-data)
      * [Futures data objects and their generic data storage objects](#futures-data-objects-and-their-generic-data-storage-objects)
         * [<a href="/sysdata/futures/instruments.py">Instruments</a>: futuresInstrument() and futuresInstrumentData()](#instruments-futuresinstrument-and-futuresinstrumentdata)
         * [<a href="/sysdata/futures/contract_dates_and_expiries.py">Contract dates</a>: contractDate()](#contract-dates-contractdate)
         * [<a href="/sysdata/futures/rolls.py">Roll cycles</a>: rollCycle()](#roll-cycles-rollcycle)
         * [<a href="/sysdata/futures/rolls.py">Roll parameters</a>: rollParameters() and rollParametersData()](#roll-parameters-rollparameters-and-rollparametersdata)
         * [<a href="/sysdata/futures/rolls.py">Contract date with roll parameters</a>: contractDateWithRollParameters()](#contract-date-with-roll-parameters-contractdatewithrollparameters)
         * [<a href="/sysdata/futures/contracts.py">Futures contracts</a>: futuresContracts() and futuresContractData()](#futures-contracts-futurescontracts-and-futurescontractdata)
         * [<a href="/sysdata/futures/futures_per_contract_prices.py">Prices for individual futures contracts</a>: futuresContractPrices(), dictFuturesContractPrices() and futuresContractPriceData()](#prices-for-individual-futures-contracts-futurescontractprices-dictfuturescontractprices-and-futurescontractpricedata)
         * [<a href="/sysdata/futures/futures_per_contract_final_prices.py">Final prices for individual futures contracts</a>: futuresContractFinalPrices(), dictFuturesContractFinalPrices()](#final-prices-for-individual-futures-contracts-futurescontractfinalprices-dictfuturescontractfinalprices)
         * [<a href="/sysdata/futures/roll_calendars.py">Roll calendars</a>: rollCalendar() and rollCalendarData()](#roll-calendars-rollcalendar-and-rollcalendardata)
         * [<a href="/sysdata/futures/multiple_prices.py">Multiple prices</a>: futuresMultiplePrices() and futuresMultiplePricesData()](#multiple-prices-futuresmultipleprices-and-futuresmultiplepricesdata)
         * [<a href="/sysdata/futures/adjusted_prices.py">Adjusted prices</a>: futuresAdjustedPrices() and futuresAdjustedPricesData()](#adjusted-prices-futuresadjustedprices-and-futuresadjustedpricesdata)
         * [<a href="/sysdata/fx/spotfx.py">Spot FX data</a>: fxPrices() and fxPricesData()](#spot-fx-data-fxprices-and-fxpricesdata)
      * [Creating your own data objects, and data storage objects; a few pointers](#creating-your-own-data-objects-and-data-storage-objects-a-few-pointers)
      * [Data storage objects for specific sources](#data-storage-objects-for-specific-sources)
         * [Static csv files used for initialisation of databases](#static-csv-files-used-for-initialisation-of-databases)
            * [csvFuturesInstrumentData()(/sysdata/csv/csv_instrument_config.py) inherits from <a href="#futuresInstrumentData">futuresInstrumentData</a>](#csvfuturesinstrumentdatasysdatacsvcsv_instrument_configpy-inherits-from-futuresinstrumentdata)
            * [<a href="/sysinit/futures/csv_data_readers/rolldata_from_csv.py">initCsvFuturesRollData()</a> inherits from <a href="#rollParametersData">rollParametersData</a>](#initcsvfuturesrolldata-inherits-from-rollparametersdata)
         * [Csv files for time series data](#csv-files-for-time-series-data)
            * [<a href="/sysdata/csv/csv_instrument_config.py">csvFuturesInstrumentData()</a> inherits from <a href="#futuresInstrumentData">futuresInstrumentData</a>](#csvfuturesinstrumentdata-inherits-from-futuresinstrumentdata)
            * [<a href="/sysdata/csv/csv_spot_fx.py">csvFxPricesData()</a> inherits from <a href="#futuresContractPriceData">futuresContractPriceData</a>](#csvfxpricesdata-inherits-from-futurescontractpricedata)
            * [<a href="/sysdata/csv/csv_roll_calendars.py">csvRollCalendarData()</a> inherits from <a href="#rollParametersData">rollParametersData</a>](#csvrollcalendardata-inherits-from-rollparametersdata)
            * [<a href="/sysdata/csv/csv_multiple_prices.py">csvFuturesMultiplePricesData()</a> inherits from <a href="#futuresMultiplePricesData">futuresMultiplePricesData</a>](#csvfuturesmultiplepricesdata-inherits-from-futuresmultiplepricesdata)
            * [<a href="/sysdata/csv/csv_adjusted_prices.py">csvFuturesAdjustedPricesData()</a> inherits from <a href="#futuresAdjustedPricesData">futuresAdjustedPricesData</a>](#csvfuturesadjustedpricesdata-inherits-from-futuresadjustedpricesdata)
            * [<a href="/sysdata/csv/csv_spot_fx.py">csvFxPricesData()</a> inherits from <a href="#fxPricesData">fxPricesData</a>](#csvfxpricesdata-inherits-from-fxpricesdata)
         * [mongo DB](#mongo-db)
            * [Specifying a mongoDB connection](#specifying-a-mongodb-connection)
            * [<a href="/sysdata/mongodb/mongo_futures_instruments.py">mongoFuturesInstrumentData()</a> inherits from <a href="#futuresInstrumentData">futuresInstrumentData</a>](#mongofuturesinstrumentdata-inherits-from-futuresinstrumentdata)
            * [<a href="/sysdata/mongodb/mongo_roll_data.py">mongoRollParametersData()</a> inherits from <a href="#rollParametersData">rollParametersData</a>](#mongorollparametersdata-inherits-from-rollparametersdata)
            * [<a href="/sysdata/mongodb/mongo_futures_contracts.py">mongoFuturesContractData()</a> inherits from <a href="#futuresContractData">futuresContractData</a>](#mongofuturescontractdata-inherits-from-futurescontractdata)
         * [Quandl](#quandl)
            * [Getting the Quandl python API](#getting-the-quandl-python-api)
            * [Setting a Quandl API key](#setting-a-quandl-api-key)
            * [<a href="/sysdata/quandl/quandl_futures.py">quandlFuturesConfiguration()</a>](#quandlfuturesconfiguration)
            * [<a href="/sysdata/quandl/quandl_futures.py">quandlFuturesContractPriceData()</a> inherits from <a href="#futuresContractPriceData">futuresContractPriceData</a>](#quandlfuturescontractpricedata-inherits-from-futurescontractpricedata)
            * [<a href="/sysdata/quandl/quandl_spotfx_prices.py">quandlFxPricesData()</a> inherits from <a href="#fxPricesData">fxPricesData</a>](#quandlfxpricesdata-inherits-from-fxpricesdata)
         * [Arctic](#arctic)
            * [Specifying an arctic connection](#specifying-an-arctic-connection)
            * [<a href="/sysdata/arctic/arctic_futures_per_contract_prices.py">arcticFuturesContractPriceData()</a> inherits from <a href="#futuresContractPriceData">futuresContractPriceData</a>](#arcticfuturescontractpricedata-inherits-from-futurescontractpricedata)
            * [<a href="/sysdata/arctic/arctic_multiple_prices.py">arcticFuturesMultiplePricesData()</a> inherits from <a href="#futuresMultiplePricesData">futuresMultiplePricesData()</a>](#arcticfuturesmultiplepricesdata-inherits-from-futuresmultiplepricesdata)
            * [<a href="/sysdata/arctic/arctic_adjusted_prices.py">arcticFuturesAdjustedPricesData()</a> inherits from <a href="#futuresAdjustedPricesData">futuresAdjustedPricesData()</a>](#arcticfuturesadjustedpricesdata-inherits-from-futuresadjustedpricesdata)
            * [<a href="/sysdata/arctic/arctic_spotfx_prices.py">arcticFxPricesData()</a> inherits from <a href="#fxPricesData">fxPricesData()</a>](#arcticfxpricesdata-inherits-from-fxpricesdata)
      * [Creating your own data storage objects for a new source](#creating-your-own-data-storage-objects-for-a-new-source)
   * [simData objects](#simdata-objects)
      * [Provided simData objects](#provided-simdata-objects)
         * [<a href="/sysdata/csv/csv_sim_futures_data.py">csvFuturesSimData()</a>](#csvfuturessimdata)
         * [<a href="/sysdata/arctic/arctic_and_mongo_sim_futures_data.py">arcticFuturesSimData()</a>](#arcticfuturessimdata)
         * [A note about multiple configuration files](#a-note-about-multiple-configuration-files)
      * [Modifying simData objects](#modifying-simdata-objects)
         * [Getting data from another source](#getting-data-from-another-source)
         * [Back-adjustment 'on the fly'](#back-adjustment-on-the-fly)
         * [Back-adjustment 'on the fly' over several days](#back-adjustment-on-the-fly-over-several-days)
      * [Constructing your own simData objects](#constructing-your-own-simdata-objects)
         * [Naming convention and inheritance](#naming-convention-and-inheritance)
         * [Multiple inheritance](#multiple-inheritance)
         * [Hooks into data storage objects](#hooks-into-data-storage-objects)
   * [Updating the provided .csv data from a production system](#updating-the-provided-csv-data-from-a-production-system)

Created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)


<a name="futures_data_workflow"></a>
# A futures data workflow

This section describes a typical workflow for setting up futures data from scratch, and setting up a mongoDB database full of the required data:

1. [Set up some static configuration information](#set_up_instrument_config) for instruments, and [roll parameters](#set_up_roll_parameter_config)
2. Get, and store, [some historical data](#get_historical_data)
3. Create, and store, [roll calendars](#roll_calendars)  (these are not actually used once multiple prices are created, so the storage is temporary)
4. Create and store ['multiple' price series](#create_multiple_prices) containing the relevant contracts we need for any given time period
5. Create and store [back-adjusted prices](#back_adjusted_prices): a single price series
6. Get, and store, [spot FX prices](#create_fx_data)

In general each step relies on the previous step to work; more formally:

- Roll parameters & Individual contract prices -> Roll calendars
- Roll calendars &  Individual contract prices -> Multiple prices
- Multiple prices -> Adjusted prices
- Instrument config, Adjusted prices, Multiple prices, Spot FX prices -> Simulation & Production data


## A note on data storage

Before we start, another note: Confusingly, data can be stored or come from various places, which include: 

1. .csv files containing data that pysystemtrade is shipped with (stored in [this set of directories](/data/futures/)); it includes everything above except for roll parameters, and is periodically updated from my own live data. Any .csv data 'pipeline' object defaults to using this data set.
2. configuration .csv files used to iniatilise the system, such as [this file](/data/futures/csvconfig/instrumentconfig.csv)
3. Temporary .csv files created in the process of initialising the databases
4. Backup .csv files, created by the production system.
5. External sources such as our broker, or data providers like Barchart and Quandl
6. Mongo DB or other databases

It's important to be clear where data is coming from, and where it is going to, during the intialisation process. Once we're actually running, the main storage will usually be in mongo DB (for production and possibly simulation).

For simulation we could just use the provided .csv files (1), and this is the default for how the backtesting part of pysystemtrade works, since you probably don't want to start down the road of building up your data stack before you've even tested out any ideas. I don't advise using .csv files for production - it won't work. As we'll see later, you can use mongoDB data for simulation and production.

Hence there are five possible use cases:

- You are happy to use the stale shipped .csv files data and are only backtesting. You don't need to do any of this!
- You want to update the .csv data used for backtests that is shipped with pysystemtrade
- You want to run backtests, but from faster databases rather than silly old .csv files, as I discuss how to do [later](#arcticfuturessimdata))
- You want to run pysystemtrade in [production](/docs/production.md), which requires database storage.
- You want both database storage and updated .csv files, maybe because you want to keep a backup of your data in .csv (someting that the production code does automatically, FWIW) or use that for backtesting

Because of this it's possible at (almost) every stage to store data in eithier .csv or databases (the exception are roll calendars, which only live in .csv format).


<a name="set_up_instrument_config"></a>
## Setting up some instrument configuration

The first step is to store some instrument configuration information. In principal this can be done in any way, but we are going to *read* from .csv files, and *write* to a [Mongo Database](https://www.mongodb.com/). There are two kinds of configuration; instrument configuration and roll configuration. Instrument configuration consists of static information that enables us to trade an instrument like EDOLLAR: the asset class, futures contract point size, and traded currency (it also includes cost levels, that are required in the simulation environment).

The relevant script to setup *information configuration* is in sysinit - the part of pysystemtrade used to initialise a new system. Here is the script you need to run [instruments_csv_mongo.py](/sysinit/futures/instruments_csv_mongo.py). Notice it uses two types of data objects: the object we write to [`mongoFuturesInstrumentData`](#mongoFuturesInstrumentData) and the object we read from [`csvFuturesInstrumentData`](#csvFuturesInstrumentData). These objects both inherit from the more generic futuresInstrumentData, and are specialist versions of that. You'll see this pattern again and again, and I describe it further in [part two of this document](#storing_futures_data). 

Make sure you are running a [Mongo Database](#mongoDB) before running this.

The information is sucked out of [this file](/data/futures/csvconfig/instrumentconfig.csv) and into the mongo database. The file includes a number of futures contracts that I don't actually trade or get prices for. Any configuration information for these may not be accurate and you use it at your own risk.

<a name="set_up_roll_parameter_config"></a>
## Roll parameter configuration

For *roll configuration* we need to initialise by running the code in this file [roll_parameters_csv_mongo.py](/sysinit/futures/roll_parameters_csv_mongo.py). Again it uses two types of data objects: we read from [a csv file](/sysinit/futures/config/rollconfig.csv) with [`initCsvFuturesRollData`](#initCsvFuturesRollData), and write to a mongo db with [`mongoRollParametersData`](#mongoRollParametersData). Again you need to make sure you are running a [Mongo Database](#mongoDB) before executing this script.

It's worth explaining the available options for roll configuration. First of all we have two *roll cycles*: 'priced' and 'hold'. Roll cycles use the usual definition for futures months (January is F, February G, March H, and the rest of the year is JKMNQUVX, with December Z). The 'priced' contracts are those that we can get prices for, whereas the 'hold' cycle contracts are those we actually hold. We may hold all the priced contracts (like for equities), or only only some because of liquidity issues (eg Gold), or to keep a consistent seasonal position (i.e. CRUDEW is Winter Crude, so we only hold December).

'RollOffsetDays': This indicates how many calendar days before a contract expires that we'd normally like to roll it. These vary from zero (Korean bonds KR3 and KR10 which you can't roll until the expiry date) up to -1100 (Eurodollar where I like to stay several years out on the curve).

'ExpiryOffset': How many days to shift the expiry date in a month, eg (the day of the month that a contract expires)-1. These values are just here so we can build roughly correct roll calendars (of which more later). In live trading you'd get the actual expiry date for each contract.

Using these two dates together will indicate when we'd ideally roll an instrument, relative to the first of the month.

For example for Bund futures, the ExpiryOffset is 6; the contract notionally expires on day 1+6 = 7th of the month. The RollOffsetDays is -5, so we roll 5 days before this. So we'd normally roll on the 1+6-5 = 2nd day of the month.

Let's take a more extreme example, Eurodollar. The ExpiryOffset is 18, and the roll offset is -1100 (no not a typo!). We'd roll this product 1100 days before it expired on the 19th day of the month.

'CarryOffset': Whether we take carry from an earlier dated contract (-1, which is preferable) or a later dated contract (+1, which isn't ideal but if we hold the front contract we have no choice). This calculation is done based on the *priced* roll cycle, so for example for winter crude where the *hold* roll cycle is just 'Z' (we hold December), and the carry offset is -1 we take the previous month in the *priced* roll cycle (which is a full year FGHJKMNQUVXZ) i.e. November (whose code is 'X'). You read more in Appendix B of [my first book](https://www.systematicmoney.org/systematic-trading).


<a name="get_historical_data"></a>
## Getting historical data for individual futures contracts

Now let's turn our attention to getting prices for individual futures contracts. 

This step is neccessary if you're going to run production code or you want newer data, newer than the data that is shipped by default. If you just want to run backtests,  but with data in a database rather than .csv, and you're not bothered about using old data, you can skip ahead to [multiple prices](#mult_adj_csv_to_arctic).

We could get this from anywhere, but I'm going to use Barchart. As you'll see, the code is quite adaptable to any kind of data source that produces .csv files. You could also use an API; in live trading we use the IB API to update our prices (Barchart also has an API but I don't support that yet). 

Once we have the data we can also store it, in principal, anywhere but I will be using the open source [Arctic library](https://github.com/manahl/arctic) which was released by my former employers [AHL](https://www.ahl.com). This sits on top of Mongo DB (so we don't need yet another database) but provides straightforward and fast storage of pandas DataFrames. Once we have the data we can also copy it to .csv files.

By the way I can't just pull down this data myself and put it on github to save you time. Storing large amounts of data in github isn't a good idea regardless of whether it is in .csv or Mongo files, and there would also be licensing issues with me basically just copying and pasting raw data that belongs to someone else. You have to get, and then store, this stuff yourself. And of course at some point in a live system you would be updating this yourself.

We'll be using [this script](sysinit/futures/barchart_futures_contract_prices.py), which in turn calls this [other more general script](sysinit/futures/contract_prices_from_csv_to_arctic.py). Although it's very specific to Barchart, with some work you should be able to adapt it. You will need to call it with the directory where your Barchart .csv files are stored.

The script does two things:

1. Rename the files so they have the name expected
2. Read in the data from the Barchart files and write them into Arctic / Mongo DB.

Barchart data (when manually downloaded through the website) is saved with the file format: `XXMYY_Barchart_Interactive_Chart*.csv`
Where XX is the two character barchart instrument identifier, eg ZW is Wheat, M is the future contract month (F=January, G=February... Z =December), YY is the two digit year code, and the rest is fluff. The little function `strip_file_names` renames them so they have the expected format: `NNNN_YYYYMMDD.csv`, where NNNN is my instrument code (at least four letters and usually way more), and YYYYMM00 is a numeric date format eg 20201200 (the last two digits are notionally the days, but these are never used - I might need them if I trade weekly expiries at some point). If I was a real programmer, I'd probably have used perl or even a bash script to do this.

The next thing we do is define the internal format of the files, by setting `barchart_csv_config`:

```python
barchart_csv_config = ConfigCsvFuturesPrices(input_date_index_name="Date Time",
                                input_skiprows=1, input_skipfooter=1,
                                input_column_mapping=dict(OPEN='Open',
                                                          HIGH='High',
                                                          LOW='Low',
                                                          FINAL='Close',
                                                          VOLUME='Volume'
                                                          ))
```

Here we can see that the barchart files have one initial row we can ignore, and one final footer row we should also ignore. The second row contains the column names; of which the `Date Time` column includes our date time index. The column mapping shows how we can map between my preferred names (in caps) and those in the file. An unused option is the `input_date_format` which defaults to `%Y-%m-%d %H:%M:%S`. Changing these options should give you flexibility to read 99% of third party data files; for others you might have to write your own parser. 

The actual reading and writing is done here:

```python
def init_arctic_with_csv_futures_contract_prices_for_code(instrument_code:str, datapath: str, csv_config = arg_not_supplied):
    print(instrument_code)
    csv_prices = csvFuturesContractPriceData(datapath, config=csv_config)
    arctic_prices = arcticFuturesContractPriceData()

    csv_price_dict = csv_prices.get_all_prices_for_instrument(instrument_code)

    for contract_date_str, prices_for_contract in csv_price_dict.items():
        print(contract_date_str)
        contract = futuresContract(instrument_code, contract_date_str)
        arctic_prices.write_prices_for_contract_object(contract, prices_for_contract, ignore_duplication=True)
```

The objects `csvFuturesContractPriceData` and `arcticFuturesContractPriceData` are 'data pipelines', which allow us to read and write a specific type of data (in this case OHLC price data for individual futures contracts). They have the same methods (and they inherit from a more generic object, futuresContractPriceData), which allows us to write code that abstracts the actual place and way the data is stored. We'll see much more of this kind of thing later.

<a name="roll_calendars"></a>
## Roll calendars

We're now ready to set up a *roll calendar*. A roll calendar is the series of dates on which we roll from one futures contract to the next. It might be helpful to read [my blog post](https://qoppac.blogspot.co.uk/2015/05/systems-building-futures-rolling.html) on rolling futures contracts (though bear in mind some of the details relate to my current trading system and do no reflect how pysystemtrade works).

You can see a roll calendar for Eurodollar futures, [here](/data/futures/roll_calendars_csv/EDOLLAR.csv). On each date we roll from the current_contract shown to the next_contract. We also see the current carry_contract; we use the differential between this and the current_contract to calculate forecasts for carry trading rules. The key thing is that on each roll date we *MUST* have prices for both the price and forward contract (we don't need carry).

There are three ways to generate roll calendars:

1. Generate a calendar based on [the individual contract data you have](#roll_calendars_from_approx). 
2. Infer the roll calendar from [existing 'multiple price' data](#roll_calendars_from_multiple). [Multiple price data](/data/futures/multiple_prices_csv) are data series that include the prices for three types of contract: the current, next, and carry contract (though of course there may be overlaps between these). pysystemtrade is shipped with .csv files for multiple and adjusted price data. Unless the multiple price data is right up to date, this may mean your rolls are a bit behind. 
3. Use the provided roll calendars, saved [here](/data/futures/roll_calendars_csv/). Again, these may be a bit behind. I generate these from multiple prices, so it's basically like step 2 except I've done the work for you.

Roll calendars are always saved as .csv files, which have the advantage of being readable and edited by human. So you can add extra rolls (if you've used method 2 or 3, and there would have been rolls since then) or do any manual hacking you need to get your multiple price data build to work. 

Once we have the roll calendar we can also adjust it so it is viable given the individual contract futures prices we have from the [previous stage](#get_historical_data). As an arbitrary example, you might assume you can roll 10 days before the expiry but that happens to be Thanksgiving so there are no prices available. The logic would find the closest date when you can actually trade. 

Then the roll calendar, plus the individual futures contract prices, can be used together to build multiple prices, from which we can get a single contionous backadjusted price series.

<a name="roll_calendars_from_approx"></a>
### Generate a roll calendar from actual futures prices

This is the method you'd use if you were really starting from scratch, and you'd just got some prices for each futures contract. The relevant script is [here](/sysinit/futures/rollcalendars_from_arcticprices_to_csv.py); you should call the function `build_and_write_roll_calendar`. It is only set up to run a single instrument at a time: creating roll calendars is careful craftmanship, not suited to a batch process.

In this script (which you should run for each instrument in turn):

- We get prices for individual futures contract [from Arctic](#arcticFuturesContractPriceData) that we created in the [previous stage](#get_historical_data)
- We get roll parameters [from Mongo](#mongoRollParametersData), that [we made earlier](#set_up_roll_parameter_config) 
- We calculate the roll calendar: 
`roll_calendar = rollCalendar.create_from_prices(dict_of_futures_contract_prices, roll_parameters)` based on the `ExpiryOffset` parameter stored in the instrument roll parameters we already setup. 
- We do some checks on the roll calendar, for monotonicity and validity (these checks will generate warnings if things go wrong)
- If we're happy with the roll calendar we [write](#csvRollCalendarData) our roll calendar into a csv file 

I strongly suggest putting an output datapath here; somewhere you can store temporary data. Otherwise you will overwrite the provided roll calendars [here](/data/futures/roll_calendars_csv/). OK, you can restore them with a git pull, but it's nice to be able to compare the 'official' and generated roll calendars.

#### Calculate the roll calendar

The actual code that generates the roll calendar is [here](sysobjects/roll_calendars.py) which mostly calls code from [here](sysinit/futures/build_roll_calendars.py):

The interesting part is:

```python
    @classmethod
    def create_from_prices(
        rollCalendar, dict_of_futures_contract_prices:dictFuturesContractFinalPrices,
            roll_parameters_object: rollParameters
    ):

        approx_calendar = generate_approximate_calendar(
            roll_parameters_object, dict_of_futures_contract_prices
        )

        adjusted_calendar = adjust_to_price_series(
            approx_calendar, dict_of_futures_contract_prices
        )

        roll_calendar = rollCalendar(adjusted_calendar)
```

So we first generate an approximate calendar, for when we'd ideally want to roll each of the contracts, based on our roll parameter `RollOffsetDays`. However we may find that there weren't *matching* prices for a given roll date. A matching price is when we have prices for both the current and next contract on the relevant day. If we don't have that, then we can't calculate an adjusted price. The *adjustment* stage finds the closest date to the ideal date (looking both forwards and backwards in time). If there are no dates with matching prices, then the process will return an error. You will need to eithier modify the roll parameters (maybe using the next rather than the previous contract), get some extra individual futures contract price data from somewhere, or manually add fake prices to your underlying futures contract prices to ensure some overlap (obviously this is cheating slightly, as without matching prices you have no way of knowing what the roll spread would have been in reality).


#### Checks

We then check that the roll calendar is monotonic and valid.

```python
    # checks - this might fail
    roll_calendar.check_if_date_index_monotonic()

    # this should never fail
    roll_calendar.check_dates_are_valid_for_prices(
        dict_of_futures_contract_prices
    )
```

A *monotonic* roll calendar will have increasing datestamps in the index. It's possible, if your data is messy, to get non-monotonic calendars. Unfortunately there is no automatic way to fix this, you need to dive in and rebuild the data (this is why I store the calendars as .csv files to make such hacking easy).

A *valid* roll calendar will have current and next contract prices on the roll date. Since we've adjusted the roll calendars so this is so they should always pass this test (if we couldn't find a date when we have aligned prices then the calendar generation would have failed with an exception).


#### Manually editing roll calendars

Roll calendars are stored in .csv format [and here is an example](/data/futures/roll_calendars_csv/EDOLLAR.csv). Of course you could put these into Mongo DB, or Arctic, but I like the ability to hack them if required; plus we only use them when starting the system up from scratch. If you have to manually edit your .csv roll calendars, you can easily load them up and check they are monotonic and valid. The function `check_saved_roll_calendar` is your friend. from [here](/sysinit/futures/rollcalendars_from_arcticprices_to_csv.py). Just make sure you are using the right datapath.


<a name="roll_calendars_from_multiple"></a>
### Roll calendars from existing 'multiple prices' .csv files

In the next section we learn how to use roll calendars, and price data for individual contracts, to create DataFrames of *multiple prices*: the series of prices for the current, forward and carry contracts; as well as the identity of those contracts. But it's also possible to reverse this operation: work out roll calendars from multiple prices.

Of course you can only do this if you've already got these prices, which means you already need to have a roll calendar: a catch 22. Fortunately there are sets of multiple prices provided in pysystemtrade, and have been for some time, [here](/data/futures/multiple_prices_csv), which I built myself.

We run [this script](/sysinit/futures/rollcalendars_from_providedcsv_prices.py) which by default will loop over all the instruments for which we have data in the multiple prices directory, and output to a provided temporary directory. 

The downside is that I don't keep the data constantly updated, and thus you might be behind. For example, if you're trading quarterly with a hold cycle of HMUZ, and the data was last updated 6 months ago, there will probably have been one or two rolls since then. You will need to manually edit the calendars to add these extra rows (in theory you could generate these automatically but it would be quite a faff, and much quicker to do it manually).


<a name="roll_calendars_from_provided"></a>
### Roll calendars shipped in .csv files

If you are too lazy even to do the previous step, I've done it for you and you can just use the calendars provided [here](/data/futures/roll_calendars_csv/EDOLLAR.csv). Of course they could also be out of date, and again you'll need to fix this manually.


<a name="create_multiple_prices"></a>
## Creating and storing multiple prices

The next stage is to create and store *multiple prices*. Multiple prices are the price and contract identifier for the current contract we're holding, the next contract we'll hold, and the carry contract we compare with the current contract for the carry trading rule. They are required for the next stage, calculating back-adjusted prices, but are also used directly by the carry trading rule in a backtest. Constructing them requires a roll calendar, and prices for individual futures contracts. You can see an example of multiple prices [here](/data/futures/multiple_prices_csv/AEX.csv). Obviously this is .csv, but the internal representation of a dataframe will look pretty similar.


### Creating multiple prices from adjusted prices

The [relevant script is here](/sysinit/futures/multipleprices_from_arcticprices_and_csv_calendars_to_arctic.py).

The script should be reasonably self explanatory in terms of data pipelines, but it's worth briefly reviewing what it does:

1. Get the roll calendars from `csv_roll_data_path` (which defaults to [this](/data/futures/roll_calendars_csv), so make sure you change it if you followed my advice to store your roll calendars somewhere else more temporary), which we have spent so much time and energy creating.
2. Get some closing prices for each individual future (we don't use OHLC data in the multiple and adjusted prices stage).
3. Optionally but recommended: adjust the roll calendar so it aligns to the closing prices. This isn't strictly neccessary if you've used method 1 above, deriving the calendar from individual futures contract prices. But it is if you've used methods 2 or 3, and strongly advisable if you've done any manual hacking of the roll calendar files. 
4. Add a 'phantom' roll a week in the future. Otherwise the data won't be complete up the present day. This will fix itself the first time you run the live production code to update prices, but some people find it annoying.
5. Create the multiple prices; basically stitching together contract data for different roll periods. 
6. Depending on flags, write the multiple prices data to`csv_multiple_data_path` (which defaults to [this](/data/futures/multiple_prices_csv)) and / or to Arctic. I like to write to both: Arctic for production, .csv as a backup and sometimes I prefer to use that for backtesting.

Step 5 can sometimes throw up warnings or outright errors if things don't look right. Sometimes you can live with these, sometimes you are better off trying to fix them by changing your roll calendar. 99.9% of the time you will have had a problem with your roll calendar that you've ignored, so it's most likely because you haven't checked your roll calendar properly: make sure it's verified, monotonic, and adjusted to actual prices.


<a name="mult_adj_csv_to_arctic"></a>
### Writing multiple prices from .csv to database

The use case here is you are happy to use the shipped .csv data, even though it's probably out of date, but you want to use a database for backtesting. You don't want to try and find and upload individual futures prices, or create roll calendars.... the good news is you don't have to. Instead you can just use [this script](/sysinit/futures/multiple_and_adjusted_from_csv_to_arctic.py) which will just copy from .csv (default ['shipping' directory](/data/futures/multiple_prices_csv)) to Arctic.

This will also copy adjusted prices, so you can now skip ahead to [creating FX data](#create_fx_data).

<a name="back_adjusted_prices"></a>
## Creating and storing back adjusted prices

Once we have multiple prices we can then create a backadjusted price series. The [relevant script](/sysinit/futures/adjustedprices_from_mongo_multiple_to_mongo.py) will read multiple prices from Arctic, do the backadjustment, and then write the prices to Arctic (and optionally to .csv if you want to use that for backup or simulation purposes). It's easy to modify this to read/write to/from different sources.


## Backadjusting 'on the fly'

It's also possible to implement the back-adjustment 'on the fly' within your backtest (which means you won't use the provided and stored adjusted prices at all). More details later in this document, [here](#back_adjust_on_the_fly).

## Changing the stitching method

The default method for stiching the prices is 'panama' stiching. If you don't like panama stitching then you can modify the method. More details later in this document, [here](#futuresAdjustedPrices).


<a name="create_fx_data"></a>
## Getting and storing FX data

Although strictly not futures prices we also need spot FX prices to run our system (unless you have a USD account and all your futures are USD denominated). The github for pysystemtrade contains spot FX data, but you will probably wish to update it. 

In live trading we'd use interactive brokers, but as an alternative for now I'm going to use one of the many free data websites: [investing.com](https://www.investing.com)

You need to register with investing.com and then download enough history. To see how much FX data there already is in the .csv data provided:

```python
from sysdata.csv.csv_spot_fx import *
data=csvFxPricesData()
data.get_fx_prices("GBPUSD")
```

Save the files in a directory with no other content, using the filename format "GBPUSD.csv". Using [this simple script](/sysinit/futures/spotfx_from_csvAndInvestingDotCom_to_arctic.py) they are written to Arctic and/or .csv files. You will need to modify the script to point to the right directory, and you can also change the column and formatting parameters to use data from other sources.

You can also run the script with `ADD_EXTRA_DATA = False, ADD_TO_CSV = True`. Then it will just do a straight copy from provided .csv data to Arctic. Your data will be stale, but in production it will automatically be updated with data from IB.


## Finished!

That's it. You've got all the price and configuration data you need to start live trading, or run backtests using the database rather than .csv files. 



<a name="Overview"></a>
# Overview of futures data in pysystemtrade

The paradigm for data storage is that we have a bunch of [data objects](#generic_objects) for specific types of data, i.e. futuresInstrument is the generic class for storing static information about instruments. Each of those objects then has a matching *data storage object* which accesses data for that object, i.e. futuresInstrumentData. Then we have [specific instances of those for different data sources](#specific_data_storage), i.e. mongoFuturesInstrumentData for storing instrument data in a mongo DB database. 

I use [data 'blobs'](/sysdata/data_blob.py) to access collections of data storage objects in both simulation and production. This also hides the exact source of the data and ensures that data objects are using a common database, logging method, and brokerage connection (since the broker is also accessed via data storage objects). More [later](#data_blobs).

For backtesting, data is accessed through `simData` objects (I discuss these [later](#simdata-objects)). These form part of the giant `system` objects that are used in backtesting ([as the `data` stage](backtesting.md#data)), and they provide the API to get certain kinds of data which are needed for backtesting (some instrument configuration and cost data, spot FX, multiple, and adjusted prices). From version 0.52 onwards `simData` objects also use data blobs.

Finally in production I use the objects in [this module](/sysproduction/data) to act as [*interfaces*](#production_interface) between production code and data blobs, so that production code doesn't need to be too concerned about the exact implementation of the data storage. These also include some business logic. 

## Heirarchy of data objects

FIXME UP TO HERE


<a name="storing_futures_data"></a>
# Storing and representing futures data

<a name="generic_objects"></a>
## Futures data objects and their generic data storage objects

<a name="futuresInstrument"></a>
### [Instruments](/sysdata/futures/instruments.py): futuresInstrument() and futuresInstrumentData()

Futures instruments are the things we actually trade, eg Eurodollar futures, but not specific contracts. Apart from the instrument code we can store *metadata* about them. This isn't hard wired into the class, but currently includes things like the asset class, cost parameters, and so on.

<a name="contractDate"></a>
### [Contract dates](/sysdata/futures/contract_dates_and_expiries.py): contractDate()

Note: There is no data storage for contract dates, they are stored only as part of [futures contracts](#futuresContracts).

A contract date allows us to identify a specific [futures contract](#futuresContracts) for a given [instrument](#futuresInstrument). Futures contracts can either be for a specific month (eg '201709') or for a specific day (eg '20170903'). The latter is required to support weekly futures contracts, or if we already know the exact expiry date of a given contract. A monthly date will be represented with trailing zeros, eg '20170900'.

We can also store expiry dates in contract dates. This can be done either by passing the exact date (which we'd do if we were getting the contract specs from our broker) or an approximate expiry offset, where 0 (the default) means the expiry is on day 1 of the relevant contract month.

<a name="rollCycle"></a>
### [Roll cycles](/sysdata/futures/rolls.py): rollCycle()

Note: There is no data storage for roll cycles, they are stored only as part of [roll parameters](#rollParameters).

Roll cycles are the mechanism by which we know how to move forwards and backwards between contracts as they expire, or when working out carry trading rule forecasts. Roll cycles use the usual definition for futures months (January is F, February G, March H, and the rest of the year is JKMNQUVX, with December Z). 

<a name="rollParameters"></a>
### [Roll parameters](/sysdata/futures/rolls.py): rollParameters() and rollParametersData()

The roll parameters include all the information we need about how a given instrument rolls:

- `hold_rollcycle` and `priced_rollcycle`. The 'priced' contracts are those that we can get prices for, whereas the 'hold' cycle contracts are those we actually hold. We may hold all the priced contracts (like for equities), or only only some because of liquidity issues (eg Gold), or to keep a consistent seasonal position (i.e. CRUDEW is Winter Crude, so we only hold December).
- `roll_offset_day`: This indicates how many calendar days before a contract expires that we'd normally like to roll it. These vary from zero (Korean bonds KR3 and KR10 which you can't roll until the expiry date) up to -1100 (Eurodollar where I like to stay several years out on the curve).
- `carry_offset`: Whether we take carry from an earlier dated contract (-1, which is preferable) or a later dated contract (+1, which isn't ideal but if we hold the front contract we have no choice). This calculation is done based on the *priced* roll cycle, so for example for winter crude where the *hold* roll cycle is just 'Z' (we hold December), and the carry offset is -1 we take the previous month in the *priced* roll cycle (which is a full year FGHJKMNQUVXZ) i.e. November (whose code is 'X'). You read more in Appendix B of [my first book](https://www.systematicmoney.org/systematic-trading) and in [my blog post](https://qoppac.blogspot.co.uk/2015/05/systems-building-futures-rolling.html).
- `approx_expiry_offset`: How many days to shift the expiry date in a month, eg (the day of the month that a contract expires)-1. These values are just here so we can build roughly correct roll calendars (of which more later). In live trading you'd get the actual expiry date for each contract.

<a name="contractDateWithRollParameters"></a>
### [Contract date with roll parameters](/sysdata/futures/rolls.py): contractDateWithRollParameters()

Note: There is no data storage for contract dates, they are stored only as part of [futures contracts](#futuresContracts).

Combining a contract date with some roll parameters means we can answer important questions like, what is the next (or previous) contract in the priced (or held) roll cycle? What is the contract I should compare this contract to when calculating carry? On what date would I want to roll this contract?

<a name="listOfFuturesContracts"></a>
<a name="futuresContracts"></a>
### [Futures contracts](/sysdata/futures/contracts.py): futuresContracts() and futuresContractData()


The combination of a specific [instrument](#futuresInstrument) and a [contract date](#contractDate) (possibly [with roll parameters](#contractDateWithRollParameters)) is a `futuresContract`. 

`listOfFuturesContracts`: This dull class exists purely so we can generate a series of historical contracts from some roll parameters.

<a name="futuresContractPrices"></a>
### [Prices for individual futures contracts](/sysdata/futures/futures_per_contract_prices.py): futuresContractPrices(), dictFuturesContractPrices() and futuresContractPriceData()


The price data for a given contract is just stored as a DataFrame with specific column names. Notice that we store Open, High, Low, and Final prices; but currently in the rest of pysystemtrade we effectively throw away everything except Final.

(A 'final' price is either a close or a settlement price depending on how the data has been parsed from it's underlying source)

`dictFuturesContractPrices`: When calculating roll calendars we work with prices from multiple contracts at once.

<a name="futuresContractFinalPrices"></a>
### [Final prices for individual futures contracts](/sysdata/futures/futures_per_contract_prices.py): futuresContractFinalPrices(), dictFuturesContractFinalPrices()

This is just the final prices alone. There is no data storage required for these since we don't need to store them separately, just extract them from either `futuresContractPrices` or `dictFuturesContractPrices` objects.

`dictFuturesContractFinalPrices`: When calculating roll calendars we work with prices from multiple contracts at once.


<a name="rollCalendar"></a>
### [Roll calendars](/sysdata/futures/roll_calendars.py): rollCalendar() and rollCalendarData()

A roll calendar is a pandas DataFrame with columns for: 

- current_contract
- next_contract
- carry_contract

Each row shows when we'd roll from holding current_contract (and using carry_contract) on to next_contract. As discussed [earlier](#roll_calendars) they can be created from a set of [roll parameters](#rollParameters) and [price data](#futuresContractPrices), or inferred from existing [multiple price data](#futuresMultiplePrices).

<a name="futuresMultiplePrices"></a>
### [Multiple prices](/sysdata/futures/multiple_prices.py): futuresMultiplePrices() and futuresMultiplePricesData()

A multiple prices object is a pandas DataFrame with columns for:PRICE, CARRY, PRICE_CONTRACT, CARRY_CONTRACT, FORWARD, and FORWARD_CONTRACT. 

We'd normally create these from scratch using a roll calendar, and some individual futures contract prices (as discussed [here](#create_multiple_prices)). Once created they can be stored and reloaded.


<a name="futuresAdjustedPrices"></a>
### [Adjusted prices](/sysdata/futures/adjusted_prices.py): futuresAdjustedPrices() and futuresAdjustedPricesData()

The representation of adjusted prices is boring beyond words; they are a pandas Series. More interesting is the fact you can create one with a back adjustment process given a [multiple prices object](#futuresMultiplePrices):

```python
from sysdata.futures.adjusted_prices import futuresAdjustedPrices
from sysdata.arctic.arctic_multiple_prices import arcticFuturesMultiplePricesData

# assuming we have some multiple prices
arctic_multiple_prices = arcticFuturesMultiplePricesData()
multiple_prices = arctic_multiple_prices.get_multiple_prices("EDOLLAR")

adjusted_prices = futuresAdjustedPrices.stich_multiple_prices(multiple_prices)
```

The adjustment defaults to the panama method. If you want to use your own stitching method then override the method `futuresAdjustedPrices.stich_multiple_prices`.


<a name="fxPrices"></a>
### [Spot FX data](/sysdata/fx/spotfx.py): fxPrices() and fxPricesData()

Technically bugger all to do with futures, but implemented in pysystemtrade as it's required for position scaling.

## Creating your own data objects, and data storage objects; a few pointers

You should store your objects in [this directory](/sysdata/futures) (for futures) or a new subdirectory of the [sysdata](/sysdata/) directory (for new asset classes). Data objects and data storage objects should live in the same file. Data objects may inherit from other objects (for example for options you might want to inherit from the underlying future), but they don't have to. Data storage objects should all inherit from [baseData](/sysdata/data.py). 

Data objects should be prefixed with the asset class if there is any potential confusion, i.e. futuresInstrument, equitiesInstrument. Data storage objects should have the same name as their data object, but with a Data suffix, eg futuresInstrumentData.

Methods you'd probably want to include in a data object:

- `create_from_dict` (`@classmethod`): Useful when reading data from a source
- `as_dict`: Useful when writing data to a source
- `create_empty` (`@classmethod`): Useful when reading data from a source if the object is unavailable, better to return one of these than throw an error in case the calling process is indifferent about missing data
- `empty`: returns True if this is an empty object

Methods you'd probably want to include in a data storage object:
 
- `keys()` and `__getitem__`. It's nice if data storage objects look like dicts. `keys()` should be mapped to `get_list_of_things_with_data`. `__getitem__` should be mapped to `get_some_data`
- `get_list_of_things_with_data`, i.e. the list of instrument codes with valid data. Should `raise NotImplementedError`
- `get_some_data`: Check to see if `is_thing_in_data` is True, then call `_get_some_data_without_checking`. If not in data, return an empty instance of the data object.
- `is_thing_in_data` i.e. is a particular instrument code in the list of codes with valid data
- `_get_some_data_without_checking`: `raise NotImplementedError`
- `delete_data_for_thing`: Check that a 'are you sure' flag is set, and that `is_thing_in_data` is True, then call `_delete_data_for_thing_without_checking`
- `_delete_data_for_thing_without_checking`: `raise NotImplementedError`
- `add_data_for_thing`: Check to see if `is_thing_in_data` is False (or that an ignore duplicates flag is set), then call `_add_data_for_thing_without_checking`
- `_add_data_for_thing_without_checking`: `raise NotImplementedError`

By the way you shouldn't actually use method names like `get_list_of_things_with_data`, that's just plain silly. Instead use `get_list_of_instruments` or what not.

Notice the use of private methods to interact with the data inside public methods that perform standard checks; these methods that actually interact with the data (rather than just mapping to other methods, or performing checks) should raise a NotImplementedError; this will then be overriden in the [data storage object for a specific data source](#specific_data_storage).

<a name="specific_data_storage"></a>
## Data storage objects for specific sources

This section covers the various sources for reading and writing [data objects](#storing_futures_data) I've implemented in pysystemtrade. 

### Static csv files used for initialisation of databases

In the initialisation part of the workflow (in [section one](#futures_data_workflow) of this document) I copied some information from .csv files to initialise a database. To acheive this we need to create some read-only access methods to the relevant .csv files (which are stored [here](/sysinit/futures/config/)).

<a name="init_instrument_config"></a>
#### csvFuturesInstrumentData()(/sysdata/csv/csv_instrument_config.py) inherits from [futuresInstrumentData](#futuresInstrumentData)

Using this script, [instruments_csv_mongo.py](/sysinit/futures/instruments_csv_mongo.py), reads instrument object data from [here](/data/futures/csvconfig/instrumentconfig.csv) using [csvFuturesInstrumentData](#csvFuturesInstrumentData). This class is not specific for initialising the database, and is also used later [for simulation data](#csvFuturesSimData).

<a name="initCsvFuturesRollData"></a>
#### [initCsvFuturesRollData()](/sysinit/futures/csv_data_readers/rolldata_from_csv.py) inherits from [rollParametersData](#rollParametersData)

Using this script, [roll_parameters_csv_mongo.py](/sysinit/futures/roll_parameters_csv_mongo.py), reads roll parameters for each instrument from [here](/sysinit/futures/config/rollconfig.csv)

<a name="csv_files"></a>
### Csv files for time series data

Storing data in .csv files has some obvious disadvantages, and doesn't feel like the sort of thing a 21st century trading system ought to be doing. However it's good for roll calendars, which sometimes need manual hacking when they're created. It's also good for the data required to run backtests that lives as part of the github repo for pysystemtrade (storing large binary files in git is not a great idea, although various workarounds exist I haven't yet found one that works satisfactorily).

For obvious (?) reasons we only implement get and read methods for .csv files (So... you want to delete the .csv file? Do it through the filesystem. Don't get python to do your dirty work for you).

<a name="csvFuturesInstrumentData"></a>
#### [csvFuturesInstrumentData()](/sysdata/csv/csv_instrument_config.py) inherits from [futuresInstrumentData](#futuresInstrumentData)

Reads futures configuration information from [here](/data/futures/csvconfig/instrumentconfig.csv) (note this is a separate file from the one used to initialise the mongoDB database [earlier](#init_instrument_config) although this uses the same class method to get the data). Columns currently used by the simulation engine are: Instrument, Pointsize, AssetClass, Currency, Slippage, PerBlock, Percentage, PerTrade. Extraneous columns don't affect functionality.

<a name="csvFuturesContractPriceData"></a>
#### [csvFxPricesData()](/sysdata/csv/csv_spot_fx.py) inherits from [futuresContractPriceData](#futuresContractPriceData)

Reads prices for individual futures contracts. There is no default directory for these as this is provided as a convenience method if you have acquired .csv contract level data and wish to put it into your system. For this reason there is a lot of flexibility in the arguments to allow different formats to be included. As an example, this code will read data downloaded from `barcharts.com` (with files renamed in the format `EDOLLAR_201509.csv`):

```python
csv_futures_contract_prices = csvFuturesContractPriceData(datapath="/home/username/data/barcharts_csv",
                                                          input_date_index_name="Date Time",
                                                          input_skiprows=1, input_skipfooter=1,
                                                          input_column_mapping=dict(OPEN='Open',
                                                                                    HIGH='High',
                                                                                    LOW='Low',
                                                                                    FINAL='Close'))
```

<a name="csvRollCalendarData"></a>
#### [csvRollCalendarData()](/sysdata/csv/csv_roll_calendars.py) inherits from [rollParametersData](#rollParametersData)

Reads roll calendars from [here](/data/futures/roll_calendars_csv). File names are just instrument names. File format is index DATE_TIME; columns: current_contract, next_contract, carry_contract. Contract identifiers should be in yyyymmdd format, with dd='00' for monthly contracts (currently weekly contracts aren't supported).

<a name="csvFuturesMultiplePricesData"></a>
#### [csvFuturesMultiplePricesData()](/sysdata/csv/csv_multiple_prices.py) inherits from [futuresMultiplePricesData](#futuresMultiplePricesData)

Reads multiple prices (the prices of contracts that are currently interesting) from [here](/data/futures/multiple_prices_csv). File names are just instrument names. File format is index DATETIME; columns: PRICE, CARRY, FORWARD, CARRY_CONTRACT, PRICE_CONTRACT, FORWARD_CONTRACT. Prices are floats. Contract identifiers should be in yyyymmdd format, with dd='00' for monthly contracts (currently weekly contracts aren't supported). 



<a name="csvFuturesAdjustedPriceData"></a>
#### [csvFuturesAdjustedPricesData()](/sysdata/csv/csv_adjusted_prices.py) inherits from [futuresAdjustedPricesData](#futuresAdjustedPricesData)

Reads back adjusted prices from [here](/data/futures/adjusted_prices_csv). File names are just instrument names. File format is index DATETIME; columns: PRICE.


<a name="csvFxPricesData"></a>
#### [csvFxPricesData()](/sysdata/csv/csv_spot_fx.py) inherits from [fxPricesData](#fxPricesData)

Reads back adjusted prices from [here](/data/futures/fx_prices_csv). File names are CC1CC2, where CC1 and CC12 are three letter ISO currency abbreviations (eg  GBPEUR). Cross rates do not have to be stored, they will be calculated on the fly. File format is index DATETIME; columns: FX.


<a name="mongoDB"></a>
### mongo DB

For production code, and storing large amounts of data (eg for individual futures contracts) we probably need something more robust than .csv files. [MongoDB](https://mongodb.com) is a no-sql database which is rather fashionable at the moment, though the main reason I selected it for this purpose is that it is used by [Arctic](#arctic). 

Obviously you will need to make sure you already have a Mongo DB instance running. You might find you already have one running, in Linux use `ps wuax | grep mongo` and then kill the relevant process.

Personally I like to keep my Mongo data in a specific subdirectory; that is achieved by starting up with `mongod --dbpath ~/data/mongodb/` (in Linux). Of course this isn't compulsory.

#### Specifying a mongoDB connection

You need to specify an IP address (host), and database name when you connect to MongoDB. These are set with the following priority:

- Firstly, arguments passed to a `mongoDb()` instance, which is then optionally passed to any data object with the argument `mongo_db=mongoDb(host='localhost', database_name='production')` All arguments are optional. 
- Then, variables set in the [private `.yaml` configuration file](/private/private_config.yaml): mongo_host, mongo_db
- Finally, default arguments in the [system defaults configuration file](/systems/provided/defaults.yaml): mongo_host, mongo_db

Note that 'localhost' is equivalent to '127.0.0.1', i.e. this machine. Note also that no port can be specified. This is because the port is hard coded in Arctic. You should stick to the default port 27017.

If your mongoDB is running on your local machine then you can stick with the defaults (assuming you are happy with the database name 'production'). If you have different requirements, eg mongo running on another machine or you want a different database name, then you should set them in the private .yaml file. If you have highly bespoke needs, eg you want to use a different database or different host for different types of data, then you will need to add code like this:

```python
# Instead of:
mfidata=mongoFuturesInstrumentData()

# Do this
from sysdata.mongodb import mongoDb
mfidata=mongoFuturesInstrumentData(mongo_db = mongoDb(database_name='another database')) # could also change host
```


<a name="mongoFuturesInstrumentData"></a>
#### [mongoFuturesInstrumentData()](/sysdata/mongodb/mongo_futures_instruments.py) inherits from [futuresInstrumentData](#futuresInstrumentData)

This stores instrument static data in a dictionary format.


<a name="mongoRollParametersData"></a>
#### [mongoRollParametersData()](/sysdata/mongodb/mongo_roll_data.py) inherits from [rollParametersData](#rollParametersData)

This stores roll parameters in a dictionary format.

<a name="mongoFuturesContractData"></a>
#### [mongoFuturesContractData()](/sysdata/mongodb/mongo_futures_contracts.py) inherits from [futuresContractData](#futuresContractData)

This stores futures contract data in a dictionary format.


### Quandl

[Quandl](https://quandl.com) is an awesome way of getting data, much of which is free, via a simple Python API. 

<a name="getQuandlPythonAPI"></a>
#### Getting the Quandl python API

At the time of writing you get this from [here](https://docs.quandl.com/docs/python-installation) (external link, may fail).

<a name="setQuandlKey"></a>
#### Setting a Quandl API key

Having a Quandl API key means you can download a fair amount of data for free without being throttled. If you have one then you should first create a file 'private_config.yaml' in the private directory of [pysystemtrade](#/private). Then add this line:

```
quandl_key: 'your_key_goes_here'
```

<a name="quandlFuturesConfiguration"></a>

#### [quandlFuturesConfiguration()](/sysdata/quandl/quandl_futures.py)

Acceses [this .csv file](/sysdata/quandl/QuandlFuturesConfig.csv) which contains the codes and markets required to get data from Quandl.

<a name="quandlFuturesContractPriceData"></a>
#### [quandlFuturesContractPriceData()](/sysdata/quandl/quandl_futures.py) inherits from [futuresContractPriceData](#futuresContractPriceData)

Reads price data and returns in the form of [futuresContractPrices](#futuresContractPrices) objects. Notice that as this is purely a source of data we don't implement write methods.


#### [quandlFxPricesData()](/sysdata/quandl/quandl_spotfx_prices.py) inherits from [fxPricesData](#fxPricesData)

DEPRECATE THIS: NO LONGER WORKS
Reads FX spot prices from QUANDL. Acceses [this .csv file](/sysdata/quandl/QuandlFXConfig.csv) which contains the codes required to get data from Quandl for a specific currency.



<a name="arctic"></a>
### Arctic 

[Arctic](https://github.com/manahl/arctic) is a superb open source time series database which sits on top of [Mongo DB](#mongoDB) and provides straightforward and fast storage of pandas DataFrames. It was created by my former colleagues at [Man AHL](https://www.ahl.com) (in fact I beta tested a very early version of Arctic), and then very generously released as open source. You don't need to run multiple instances of Mongo DB when using my data objects for Mongo DB and Arctic, they use the same one. However we configure them separately; the configuration for Arctic objects is [here](/sysdata/arctic/arctic_connection.py) (so in theory you could use two instances on different machines with separate host names).

Basically my mongo DB objects are for storing static information, whilst Arctic is for time series.

Arctic has several *storage engines*, in my code I use the default VersionStore.

#### Specifying an arctic connection

You need to specify an IP address (host), and database name when you connect to Arctic. Usually Arctic data objects will default to using the same settings as Mongo data objects.

Note:
- No port is specified - Arctic can only use the default port. For this reason I strongly discourage changing the port used when connecting to other mongo databases.
- In actual use Arctic prepends 'arctic-' to the database name. So instead of 'production' it specifies 'arctic-production'. This shouldn't be an issue unless you are connecting directly to the mongo database.

These are set with the following priority:

- Firstly, arguments passed to a `mongoDb()` instance, which is then optionally passed to any Arctic data object with the argument `mongo_db=mongoDb(host='localhost', database_name='production')` All arguments are optional. 
- Then, arguments set in the [private `.yaml` configuration file](/private/private_config.yaml): mongo_host, mongo_db
- Finally, default arguments hardcoded [in mongo_connection.py](/sysdata/mongodb/mongo_connection.py): DEFAULT_MONGO_DB, DEFAULT_MONGO_HOST, DEFAULT_MONGO_PORT

Note that 'localhost' is equivalent to '127.0.0.1', i.e. this machine.

If your mongoDB is running on your local machine with the standard port settings, then you can stick with the defaults (assuming you are happy with the database name 'production'). If you have different requirements, eg mongo running on another machine, then you should code them up in the private .yaml file. If you have highly bespoke needs, eg you want to use a different database for different types of data, then you will need to add code like this:

```python
# Instead of:
afcpdata=arcticFuturesContractPriceData()

# Do this
from sysdata.mongodb import mongoDb
afcpdata=arcticFuturesContractPriceData(mongo_db = mongoDb(database_name='another database')) # could also change host
```


<a name="arcticFuturesContractPriceData"></a>
#### [arcticFuturesContractPriceData()](/sysdata/arctic/arctic_futures_per_contract_prices.py) inherits from [futuresContractPriceData](#futuresContractPriceData)

Read and writes per contract futures price data.

#### [arcticFuturesMultiplePricesData()](/sysdata/arctic/arctic_multiple_prices.py) inherits from [futuresMultiplePricesData()](#futuresMultiplePricesData)

Read and writes multiple price data for each instrument.

#### [arcticFuturesAdjustedPricesData()](/sysdata/arctic/arctic_adjusted_prices.py) inherits from [futuresAdjustedPricesData()](#futuresAdjustedPricesData)

Read and writes adjusted price data for each instrument.

#### [arcticFxPricesData()](/sysdata/arctic/arctic_spotfx_prices.py) inherits from [fxPricesData()](#fxPricesData)

Read and writes spot FX data for each instrument.

## Creating your own data storage objects for a new source

Creating your own data storage objects is trivial, assuming they are for an existing kind of data object. 

They should live in a subdirectory of [sysdata](/sysdata), named for the data source i.e. [sysdata/arctic](/sysdata/arctic).

Look at an existing data storage object for a different source to see which methods you'd need to implement, and to see the generic data storage object you should inherit from. Normally you'd need to override all the methods in the generic object which return `NotImplementedError`; the exception is if you have a read-only source like Quandl, or if you're working with .csv or similar files in which case I wouldn't recommend implementing delete methods.

Use the naming convention sourceNameOfGenericDataObject, i.e. `class arcticFuturesContractPriceData(futuresContractPriceData)`. 

For databases you may want to create connection objects (like [this](#/sysdata/arctic/arctic_connection.py) for Arctic) 


<a name="data_blobs"></a>
# Data blobs

TO DO



<a name="simData_objects"></a>
# simData objects

The `simData` object is a compulsory part of the psystemtrade system object which runs simulations (or in live trading generates desired positions). The API required for that is laid out in the userguide, [here](/docs/userguide.md#using-the-standard-data-objects). For maximum flexibility as of version 0.17 these objects are in turn constructed of methods that hook into data storage objects for specific sources. So for example in the default [`csvFuturesSimData`](/sysdata/csv/csv_sim_futures_data.py) the compulsory method (for futures) get_backadjusted_futures_price is hooked into an instance of `csvFuturesAdjustedPricesData`.

This modularity allows us to easily replace the data objects, so we could load our adjusted prices from mongo DB, or do 'back adjustment' of futures prices 'on the fly'.

For futures simData objects need to know the source of:

- back adjusted prices
- multiple price data
- spot FX prices
- instrument configuration and cost information

Direct access to other kinds of information isn't neccessary for simulations.

## Provided simData objects

I've provided two complete simData objects which get their data from different sources: [csvSimData](#csvSimData) and [mongoSimData](#mongoSimData).

<a name="csvFuturesSimData"></a>
### [csvFuturesSimData()](/sysdata/csv/csv_sim_futures_data.py)

The simplest simData object gets all of its data from .csv files, making it ideal for simulations if you haven't built a process yet to get your own data. It's essentially a like for like replacement for the simpler csvSimData objects that pysystemtrade used in versions before 0.17.0.

<a name="mongoSimData"></a>
### [arcticFuturesSimData()](/sysdata/arctic/arctic_and_mongo_sim_futures_data.py)

This is a simData object which gets it's data out of Mongo DB (static) and Arctic (time series) (*Yes the class name should include both terms. Yes I shortened it so it isn't ridiculously long, and most of the interesting stuff comes from Arctic*). It is better for live trading.

Because the mongoDB data isn't included in the github repo, before using this you need to write the required data into Mongo and Arctic.
You can do this from scratch, as per the ['futures data workflow'](#a-futures-data-workflow) at the start of this document:

- [Instrument configuration and cost data](#setting-up-some-instrument-configuration)
- [Adjusted prices](#creating-and-storing-back-adjusted-prices)
- [Multiple prices](#creating-and-storing-multiple-prices)
- [Spot FX prices](#create_fx_data)

Alternatively you can run the following scripts which will copy the data from the existing github .csv files:

- [Instrument configuration and cost data](/sysinit/futures/repocsv_instrument_config.py)
- [Adjusted prices](/sysinit/futures/repocsv_adjusted_prices.py)
- [Multiple prices](/sysinit/futures/repocsv_multiple_prices.py)
- [Spot FX prices](/sysinit/futures/repocsv_spotfx_prices.py)

Of course it's also possible to mix these two methods. Once you have the data it's just a matter of replacing the default csv data object:

```python
from systems.provided.futures_chapter15.basesystem import futures_system
from sysdata.arctic.arctic_and_mongo_sim_futures_data import arcticFuturesSimData
system = futures_system(data = arcticFuturesSimData(), log_level="on")
print(system.accounts.portfolio().sharpe())
```
### A note about multiple configuration files

Configuration information about futures instruments is stored in a number of different places:

- Instrument configuration and cost levels in this [.csv file](/data/futures/csvconfig/instrumentconfig.csv), used by default with `csvFuturesSimData` or will be copied to the database with [this script](/sysinit/futures/repocsv_instrument_config.py)
- Roll configuration information in [this .csv file](/sysinit/futures/config/rollconfig.csv), which will be copied to Mongo DB with [this script](/sysinit/futures/roll_parameters_csv_mongo.py)
- Interactive brokers configuration in [this file]() and [this file](https://github.com/robcarver17/pysystemtrade/blob/master/sysbrokers/IB/ibConfigSpotFX.csv) and [this file](https://github.com/robcarver17/pysystemtrade/blob/master/sysbrokers/IB/ibConfigFutures.csv).

The instruments in these lists won't neccessarily match up, however under DRY there shouldn't be duplicated column headings across files.

The `system.get_instrument_list()` method is used by the simulation to decide which markets to trade; if no explicit list of instruments is included then it will fall back on the method `system.data.get_instrument_list()`. In both the provided simData objects this will resolve to the method `get_instrument_list` in the class which gets back adjusted prices, or in whatever overrides it for a given data source (.csv or Mongo DB). In practice this means it's okay if your instrument configuration (or roll configuration, when used) is a superset of the instruments you have adjusted prices for. But it's not okay if you have adjusted prices for an instrument, but no configuration information.

<a name="modify_SimData"></a>
## Modifying simData objects

Constructing simData objects in the way I've done makes it relatively easy to modify them. Here are a few examples.

### Getting data from another source

Let's suppose you want to use Arctic and Mongo DB data, but get your spot FX prices from a .csv file. OK this is a silly example, but hopefully it will be easy to generalise this to doing more sensible things. Modify the file [arctic_and_mongo_sim_futures_data.py](/sysdata/arctic/arctic_and_mongo_sim_futures_data.py):

```python
# add import
from sysdata.csv.csv_sim_futures_data import csvFXData

# replace this class: class arcticFuturesSimData()
# with:

class arcticFuturesSimData(csvFXData, arcticFuturesAdjustedPriceSimData,
                           mongoFuturesConfigDataForSim, arcticFuturesMultiplePriceSimData):

    def __repr__(self):
        return "arcticFuturesSimData for %d instruments getting FX data from csv land" % len(self.get_instrument_list())


```

If you want to specify a custom .csv directory or you'll also need to write a special __init__ class to achieve that (bearing in mind that these are specified in the __init__ for `csvPaths` and `dbconnections`, which ultimately are both inherited by `arcticFuturesSimData`)- I haven't tried it myself.

<a name="back_adjust_on_the_fly"></a>
### Back-adjustment 'on the fly'

This is a modification to csvSimData which calculates back adjustment prices 'on the fly', rather than getting them pre-loaded from another database. This would allow you to use different back adjustments and see what effects they had. Note that this will work 'out of the box' for any 'single point' back adjustment where the roll happens on a single day, and where you can use multiple price data (which we already have). For any back adjustment where the process happens over several days you'd need to add extra methods to access individual futures contract prices and roll calendars. This is explained [in the next section](#back_adjust_on_the_fly_multiple_days).

Create a new class:
```python
from sysdata.futures.futuresDataForSim import futuresAdjustedPriceData, futuresAdjustedPrice
from sysdata.futures.adjusted_prices import futuresAdjustedPrices

class backAdjustOnTheFly(futuresAdjustedPriceData):
    def get_backadjusted_futures_price(self, instrument_code):
        multiple_prices = self._get_all_price_data(instrument_code)
        adjusted_prices = futuresAdjustedPrices.stitch_multiple_prices(multiple_prices)

        return adjusted_prices
```

In the file [csv_sim_futures_data](/sysdata/csv/csv_sim_futures_data.py) replace: 

```python
class csvFuturesSimData(csvFXData, csvFuturesAdjustedPriceData, csvFuturesConfigDataForSim, csvFuturesMultiplePriceData):
```

with:

```python
class csvFuturesSimData(csvFXData, backAdjustOnTheFly, csvFuturesConfigDataForSim, csvFuturesMultiplePriceData):
```

If you want to test different adjustment techniques other than the default 'Panama stitch', then you need to override `futuresAdjustedPrices.stitch_multiple_prices()`.


<a name="back_adjust_on_the_fly_multiple_days"></a>
### Back-adjustment 'on the fly' over several days
For any back adjustment where the process happens over multiple days you'd need to add extra methods to access individual futures contract prices and roll calendars. Let's suppose we want to get these from Arctic (prices) and .csv files (roll calendars).


You'll need to override `futuresAdjustedPrices.stitch_multiple_prices()` so it uses roll calendars and individual contract; I assume you inherit from futuresAdjustedPrices and have a new class with the override: `futuresAdjustedPricesExtraData`. Then create the following classes:

```python
from sysdata.futures.futuresDataForSim import futuresAdjustedPriceData, futuresAdjustedPrice
from somewhere import futuresAdjustedPricesExtraData # you need to provide this yourself
from sysdata.arctic.arctic_futures_per_contract_prices import arcticFuturesContractPriceData
from sysdata.csv.csv_roll_calendars import csvRollCalendarData

class backAdjustOnTheFlyExtraData(futuresAdjustedPriceData):
    def get_backadjusted_futures_price(self, instrument_code):
        individual_contract_prices = self._get_individual_contract_prices(instrument_code)
        roll_calendar = self._get_roll_calendar(instrument_code)
        adjusted_prices = futuresAdjustedPricesExtraData.stich_multiple_prices(roll_calendar, individual_contract_prices)

        return adjusted_prices

class arcticContractPricesForSim():
    def _get_individual_contract_prices(instrument_code):
        arctic_contract_prices_data_object = self._get_arctic_contract_prices_data_object()
        
        return arctic_contract_prices_data_object.get_all_prices_for_instrument(instrument_code)

    def _get_arctic_contract_prices_data_object(self):
        # this will just use the default connection but you change if you like
        arctic_contract_prices_data_object = arcticFuturesContractPriceData()
        arctic_contract_prices_data_object.log = self.log
        return arctic_contract_prices_data_object

class csvRollCalendarForSim():
    def _get_roll_calendar(self, instrument_code):
        roll_calendar_data_object = self.__get_csv_roll_calendar_data_object()
        
        return roll_calendar_data_object.get_roll_calendar(instrument_code)

    def _get_csv_roll_calendar_data_object(self):
        pathname =self._resolve_path("roll_calendars")
        roll_calendar_data_object  = csvRollCalendarData(data_path)
        roll_calendar_data_object.log = self.log

        return roll_calendar_data_object 

```


In the file [csv_sim_futures_data](/sysdata/csv/csv_sim_futures_data.py) replace: 

```python
class csvFuturesSimData(csvFXData, csvFuturesAdjustedPriceData, csvFuturesConfigDataForSim, csvFuturesMultiplePriceData):
```

with:

```python
class csvFuturesSimData(csvFXData, backAdjustOnTheFlyExtraData, csvRollCalendarForSim, arcticContractPricesForSim, csvFuturesConfigDataForSim, csvFuturesMultiplePriceData):
```


## Constructing your own simData objects

If you want to construct your own simData objects it's worth understanding their detailed internals in a bit more detail.

### Naming convention and inheritance

The base class is [simData](/sysdata/data.py). This in turn inherits from baseData, which is also the parent class for the [data storage objects](#storing_futures_data) described earlier in this document. simData implements a number of compulsory methods that we need to run simulations. These are described in more detail in the main [user guide](/docs/userguide.md#data) for pysystemtrade.

We then inherit from simData for a specific asset class implementation, i.e. for futures we have the method futuresSimData in [futuresDataForSim.py](/sysdata/futures/futuresDataForSim.py). This adds methods for additional types of data (eg carry) but can also override methods (eg get_raw_price is overriden so it gets backadjusted futures prices).

We then inherit for specific data source implementations. For .csv files we have the method csvSimFuturesData in [csv_sim_futures_data.py](/sysdata/csv/csv_sim_futures_data.py).

Notice the naming convention: sourceAssetclassSimData.

### Multiple inheritance

Because they are quite complex I've broken down the futures simData objects into sub-classes, bringing everything back together with multiple inheritance in the final simData classes we actually use.

So for futures we have the following classes in [futuresDataForSim.py](/sysdata/futures/futuresDataForSim.py), which are generic regardless of source (all inheriting from simData):

1. futuresAdjustedPriceData(simData)
2. futuresMultiplePriceData(simData)
3. futuresConfigDataForSim(simData)
4. futuresSimData: This class is redundant for reasons that will become obvious below

Then for csv files we have the following in [csv_sim_futures_data.py](/sysdata/csv/csv_sim_futures_data.py):

1. csvPaths(simData): To ensure consistent resolution of path names when locating .csv files
2. csvFXData(csvPaths, simData): Covers methods unrelated to futures, so directly inherits from the base simData class
3. csvFuturesConfigDataForSim(csvPaths, futuresConfigDataForSim)
4. csvFuturesAdjustedPriceData(csvPaths, futuresAdjustedPriceData)
5. csvMultiplePriceData(csvPaths, futuresMultiplePriceData)
6. csvFuturesSimData(csvFXData, csvFuturesAdjustedPriceData, csvFuturesConfigDataForSim, csvMultiplePriceData)

Classes 3,4 and 5 each inherit from one of the futures sub classes (class 2 bypasses the futures specific classes and inherits directly from simData - strictly speaking we should probably have an fxSimData class in between these). Then class 6 ties all these together. Notice that futuresSimData isn't referenced anywhere; it is included only as a template to show how you should do this 'gluing' together.

### Hooks into data storage objects

The methods we write for specific sources to override the methods in simData or simFuturesData type objects should all 'hook' into a [data storage object for the appropriate source](#specific_data_storage). I suggest using common methods to get the relevant data storage object, and to look up path names or otherwise configure the storage options (eg database hostname).

Eg here is the code for csvFuturesMultiplePriceData in [csv_sim_futures_data.py](/sysdata/csv/csv_sim_futures_data.py), with additional annotations:

```python
class csvMultiplePriceData(csvPaths, futuresMultiplePriceData):
    def _get_all_price_data(self, instrument_code): # overides a method in futuresMultiplePriceData
        csv_multiple_prices_data = self._get_all_prices_data_object() # get a data storage object (see method below)
        instr_all_price_data = csv_multiple_prices_data.get_multiple_prices(instrument_code) # Call relevant method of data storage object

        return instr_all_price_data

    def _get_all_prices_data_object(self): # data storage object

        pathname = self._resolve_path("multiple_price_data") # call to csvPaths class method to get path

        csv_multiple_prices_data = csvFuturesMultiplePricesData(datapath=pathname) # create a data storage object for .csv files with the pathname
        csv_multiple_prices_data.log = self.log # ensure logging is consistent

        return csv_multiple_prices_data # return the data storage object instance


```

<a name="production_interface"></a>
# Production code data interface

TO DO