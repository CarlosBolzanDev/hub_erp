using System.Diagnostics;

namespace VoltPy.Runtime;

public sealed record PythonExecutionResult(int ExitCode, TimeSpan Duration);

/// <summary>
/// Hospeda o CPython embutido via subprocess nesta versão inicial.
/// A configuração limpa PATH/PYTHON* para não depender do Python global do Windows.
/// </summary>
public sealed class PythonRuntimeHost
{
    private readonly VoltPyPaths _paths;
    private readonly IVoltPyLogger _logger;
    private readonly PythonRuntimeOptions _options;

    public PythonRuntimeHost(VoltPyPaths paths, IVoltPyLogger logger, PythonRuntimeOptions? options = null)
    {
        _paths = paths;
        _logger = logger;
        _options = options ?? new PythonRuntimeOptions();
    }

    public async Task<PythonExecutionResult> ExecuteScriptAsync(string scriptPath, IReadOnlyDictionary<string, string>? environment = null, CancellationToken cancellationToken = default)
    {
        if (!File.Exists(scriptPath))
        {
            throw new FileNotFoundException("O entrypoint Python do app não foi encontrado.", scriptPath);
        }

        var python = ResolvePythonExecutable();
        var startInfo = CreateStartInfo(python, $"\"{_paths.BootstrapScript}\" \"{scriptPath}\"", Path.GetDirectoryName(scriptPath)!);
        if (environment is not null)
        {
            foreach (var item in environment)
            {
                startInfo.Environment[item.Key] = item.Value;
            }
        }

        _logger.Info($"Inicializando runtime Python: {python}");
        _logger.Info($"Executando script: {scriptPath}");

        var stopwatch = Stopwatch.StartNew();
        using var process = new Process { StartInfo = startInfo, EnableRaisingEvents = true };
        process.OutputDataReceived += (_, e) => { if (!string.IsNullOrWhiteSpace(e.Data)) _logger.Info($"python stdout: {e.Data}"); };
        process.ErrorDataReceived += (_, e) => { if (!string.IsNullOrWhiteSpace(e.Data)) _logger.Error($"python stderr: {e.Data}"); };

        process.Start();
        process.BeginOutputReadLine();
        process.BeginErrorReadLine();
        await process.WaitForExitAsync(cancellationToken);
        stopwatch.Stop();

        _logger.Info($"Script finalizado com código {process.ExitCode} em {stopwatch.Elapsed}.");
        return new PythonExecutionResult(process.ExitCode, stopwatch.Elapsed);
    }

    private string ResolvePythonExecutable()
    {
        if (File.Exists(_paths.PythonExecutable))
        {
            return _paths.PythonExecutable;
        }

        if (_options.UseSystemPythonFallback)
        {
            _logger.Warning("Fallback para python do sistema ativado apenas para desenvolvimento.");
            return OperatingSystem.IsWindows() ? "python.exe" : "python3";
        }

        throw new FileNotFoundException("Runtime Python embutido ausente. Configure RuntimeDirectory/PythonExecutable para apontar para a instalação externa VoltPyRuntime.", _paths.PythonExecutable);
    }

    private ProcessStartInfo CreateStartInfo(string pythonExecutable, string arguments, string workingDirectory)
    {
        var pythonPath = new[]
        {
            _paths.NamespaceDirectory,
            _paths.SitePackages,
            _paths.PythonLib
        }.Concat(_options.AdditionalPythonPath).Distinct(StringComparer.OrdinalIgnoreCase);

        var startInfo = new ProcessStartInfo
        {
            FileName = pythonExecutable,
            Arguments = arguments,
            WorkingDirectory = workingDirectory,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = _options.HiddenWindow,
        };

        startInfo.Environment["PYTHONHOME"] = _paths.PythonHome;
        startInfo.Environment["PYTHONPATH"] = string.Join(Path.PathSeparator, pythonPath);
        startInfo.Environment["PYTHONNOUSERSITE"] = "1";
        startInfo.Environment["PYTHONDONTWRITEBYTECODE"] = "1";
        startInfo.Environment["VOLTPY_ROOT"] = _paths.RootDirectory;
        startInfo.Environment["VOLTPY_NAMESPACE"] = _paths.NamespaceDirectory;
        startInfo.Environment["VOLTPY_PACKAGES"] = _paths.PackagesDirectory;
        startInfo.Environment["VOLTPY_LOGS"] = _paths.LogsDirectory;
        startInfo.Environment["VOLTPY_RUNTIME"] = _paths.RuntimeDirectory;
        startInfo.Environment["VOLTPY_APPS"] = _paths.AppsDirectory;
        startInfo.Environment["VOLTPY_TEMP"] = _paths.TempDirectory;
        startInfo.Environment.Remove("PYTHONSTARTUP");

        return startInfo;
    }
}
