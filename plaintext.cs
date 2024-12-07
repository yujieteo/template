using System;
using System.IO;

class Program
{
    private static string[] Example()
    {
        const int numLines = 4;
        string[] lines = new string[numLines]
        {
            "XX"
            "XX",
            "XX",
            "XX"
        };
        const string filePath = "xx.txt";
        WriteToFile(lines, filePath);
        return lines;
    }

    private static void WriteToFile(string[] lines, string filePath)
    {
        try
        {
            File.WriteAllLines(filePath, lines);
        }
        catch (IOException ioEx)
        {
            HandleFileError(ioEx);
        }
        catch (UnauthorizedAccessException uaEx)
        {
            HandleAccessError(uaEx);
        }
        catch (Exception ex)
        {
            HandleGeneralError(ex);
        }
    }

    private static void HandleFileError(IOException ex)
    {
        Console.WriteLine("File error: " + ex.Message);
    }

    private static void HandleAccessError(UnauthorizedAccessException ex)
    {
        Console.WriteLine("Access error: " + ex.Message);
    }

    private static void HandleGeneralError(Exception ex)
    {
        Console.WriteLine("An error occurred: " + ex.Message);
    }

    static void Main(string[] args)
    {
        Example();
    }
}
