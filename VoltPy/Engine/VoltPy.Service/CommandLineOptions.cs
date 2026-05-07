namespace VoltPy.Service;

public sealed record CommandLineOptions(
    string AppName,
    string? EngineDirectory,
    string? ConfigFile,
    bool DevPythonFallback,
    bool Supervise)
{
    public static CommandLineOptions Parse(string[] args)
    {
        var appName = ".";
        string? engineDirectory = null;
        string? configFile = null;
        var devFallback = false;
        var supervise = false;

        for (var index = 0; index < args.Length; index++)
        {
            var arg = args[index];
            switch (arg)
            {
                case "--engine-dir":
                    engineDirectory = RequireValue(args, ref index, arg);
                    break;
                case "--config":
                    configFile = RequireValue(args, ref index, arg);
                    break;
                case "--dev-python-fallback":
                    devFallback = true;
                    break;
                case "--supervise":
                    supervise = true;
                    break;
                default:
                    if (!arg.StartsWith("--", StringComparison.Ordinal))
                    {
                        appName = arg;
                    }
                    break;
            }
        }

        return new CommandLineOptions(appName, engineDirectory, configFile, devFallback, supervise);
    }

    private static string RequireValue(string[] args, ref int index, string option)
    {
        if (index + 1 >= args.Length || args[index + 1].StartsWith("--", StringComparison.Ordinal))
        {
            throw new ArgumentException($"A opção {option} exige um valor.");
        }

        index++;
        return args[index];
    }
}
