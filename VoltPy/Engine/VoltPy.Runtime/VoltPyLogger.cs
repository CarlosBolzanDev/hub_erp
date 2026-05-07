namespace VoltPy.Runtime;

public interface IVoltPyLogger
{
    void Info(string message);
    void Warning(string message);
    void Error(string message, Exception? exception = null);
}

/// <summary>
/// Logger simples, sem dependências externas, próprio para a primeira versão da engine.
/// Escreve logs em arquivo e, quando há console anexado, também no stdout/stderr.
/// </summary>
public sealed class FileVoltPyLogger : IVoltPyLogger
{
    private readonly string _logFile;
    private readonly object _sync = new();

    public FileVoltPyLogger(VoltPyPaths paths, string component)
    {
        Directory.CreateDirectory(paths.LogsDirectory);
        _logFile = Path.Combine(paths.LogsDirectory, $"{component}-{DateTimeOffset.UtcNow:yyyyMMdd}.log");
    }

    public void Info(string message) => Write("INFO", message, null);
    public void Warning(string message) => Write("WARN", message, null);
    public void Error(string message, Exception? exception = null) => Write("ERROR", message, exception);

    private void Write(string level, string message, Exception? exception)
    {
        var line = $"{DateTimeOffset.UtcNow:O} [{level}] {message}";
        if (exception is not null)
        {
            line += Environment.NewLine + exception;
        }

        lock (_sync)
        {
            File.AppendAllText(_logFile, line + Environment.NewLine);
        }

        if (!OperatingSystem.IsWindows())
        {
            var writer = level == "ERROR" ? Console.Error : Console.Out;
            writer.WriteLine(line);
        }
    }
}
