using VoltPy.Loader;
using VoltPy.Packages;
using VoltPy.Runtime;

namespace VoltPy.Service;

/// <summary>
/// Serviço/runtime em background sem dependências externas. Em produção pode ser
/// instalado por um wrapper de Windows Service apontando para VoltPy.Service.exe.
/// </summary>
public sealed class VoltPyService
{
    private readonly VoltPyPaths _paths;
    private readonly IVoltPyLogger _logger;
    private readonly AppExecutor _executor;

    public VoltPyService(VoltPyPaths paths, IVoltPyLogger logger, AppExecutor executor)
    {
        _paths = paths;
        _logger = logger;
        _executor = executor;
    }

    public static VoltPyService Create(bool devPythonFallback = false)
    {
        var paths = VoltPyPaths.Discover(Environment.CurrentDirectory);
        paths.EnsureBaseDirectories();
        var logger = new FileVoltPyLogger(paths, "service");
        var runtimeHost = new PythonRuntimeHost(paths, logger, new PythonRuntimeOptions
        {
            HiddenWindow = true,
            UseSystemPythonFallback = devPythonFallback,
        });
        var packageManager = new PackageManager(paths, logger);
        var executor = new AppExecutor(paths, new ManifestLoader(), packageManager, runtimeHost, logger);
        return new VoltPyService(paths, logger, executor);
    }

    public async Task<int> RunOnceAsync(string appName, CancellationToken cancellationToken = default)
    {
        _logger.Info("VoltPy.Service iniciado em modo run-once.");
        return await _executor.ExecuteAsync(appName, cancellationToken);
    }

    public async Task<int> RunSupervisorAsync(string appName, TimeSpan restartDelay, CancellationToken cancellationToken = default)
    {
        _logger.Info($"VoltPy.Service iniciado em background supervisionando {appName}.");
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                var code = await _executor.ExecuteAsync(appName, cancellationToken);
                _logger.Warning($"App {appName} finalizou com código {code}; reiniciando em {restartDelay}.");
            }
            catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
            {
                break;
            }
            catch (Exception ex)
            {
                _logger.Error($"Falha ao executar {appName}; reiniciando em {restartDelay}.", ex);
            }

            await Task.Delay(restartDelay, cancellationToken);
        }

        _logger.Info("VoltPy.Service encerrado.");
        return 0;
    }
}
