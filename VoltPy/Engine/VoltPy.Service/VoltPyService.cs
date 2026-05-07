using VoltPy.Loader;
using VoltPy.Packages;
using VoltPy.Runtime;

namespace VoltPy.Service;

/// <summary>
/// Serviço/runtime em background sem dependências externas. O host pode ficar em
/// uma pasta própria e apontar para uma instalação externa VoltPyRuntime via
/// VoltPy/config/runtime.json, VOLTPY_ENGINE_DIR ou --engine-dir.
/// </summary>
public sealed class VoltPyService
{
    private readonly IVoltPyLogger _logger;
    private readonly AppExecutor _executor;

    public VoltPyService(IVoltPyLogger logger, AppExecutor executor)
    {
        _logger = logger;
        _executor = executor;
    }

    public static VoltPyService Create(CommandLineOptions options)
    {
        var configuration = VoltPyConfigurationLoader.Load(options.ConfigFile, options.EngineDirectory, AppContext.BaseDirectory);
        var logger = new FileVoltPyLogger(configuration.Paths, "service");
        var runtimeHost = new PythonRuntimeHost(configuration.Paths, logger, configuration.RuntimeOptions with
        {
            UseSystemPythonFallback = options.DevPythonFallback || configuration.RuntimeOptions.UseSystemPythonFallback,
        });
        var packageManager = new PackageManager(configuration.Paths, logger);
        var executor = new AppExecutor(configuration.Paths, new ManifestLoader(), packageManager, runtimeHost, logger);

        logger.Info($"Host configurado. Fonte={configuration.SourceFile ?? "env/cli"}; Engine={configuration.Paths.EngineDirectory}; App={configuration.Paths.AppDirectory}; Namespace={configuration.Paths.NamespaceDirectory}.");
        return new VoltPyService(logger, executor);
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
