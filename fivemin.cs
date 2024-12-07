using System;
using System.IO;

class Program
{
    private const string FILE_NAME = "times.txt";
    private const int MAX_TIME_INTERVALS = 288;
    private const int TIME_INCREMENT = 5;
    private const int MAX_MINUTES_IN_HOUR = 60;
    private const int HOURS_IN_DAY = 24;

    static void writeTime(StreamWriter file, int time)
    {
        file.WriteLine(string.Format("{0:D4}, Event", time));
    }

    static int incrementTime(int time)
    {
        int hours = time / 100;
        int minutes = time % 100;

        minutes += TIME_INCREMENT;
        if (minutes >= MAX_MINUTES_IN_HOUR)
        {
            minutes = 0;
            hours = (hours + 1) % HOURS_IN_DAY;
        }

        return (hours * 100) + minutes;
    }

    static StreamWriter getStreamWriter(string fileName)
    {
        return new StreamWriter(fileName);
    }

    static void generateTimes(StreamWriter file, int maxTimeIntervals)
    {
        int currentTime = 0;
        for (int i = 0; i < maxTimeIntervals; i++)
        {
            writeTime(file, currentTime);
            currentTime = incrementTime(currentTime);
        }
    }

    static void Main()
    {
        using (StreamWriter file = getStreamWriter(FILE_NAME))
        {
            generateTimes(file, MAX_TIME_INTERVALS);
        }

        Console.WriteLine("File has been written successfully.");
    }
}
