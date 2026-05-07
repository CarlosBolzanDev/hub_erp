using VoltPy.Packages;
using VoltPy.Runtime;

namespace VoltPy.Loader;

public sealed class AppExecutor
{
    private readonly VoltPyPaths _paths;
    private readonly ManifestLoader _manifestLoader;
    private readonly IPackageManager _packageManager;
    private readonly PythonRuntimeHost _runtimeHost;
    private readonly IVoltPyLogger _logger;

    public AppExecutor(VoltPyPaths paths, ManifestLoader manifestLoader, IPackageManager packageManager, PythonRuntimeHost runtimeHost, IVoltPyLogger logger)
    {
        _paths = paths;
        _manifestLoader = manifestLoader;
        _packageManager = packageManager;
        _runtimeHost = runtimeHost;
        _logger = logger;
    }

    public async Task<int> ExecuteAsync(string? appPathOrEntry = null, CancellationToken cancellationToken = default)
    {
        var (appDirectory, explicitEntry) = ResolveAppTarget(appPathOrEntry);
        var manifest = _manifestLoader.LoadOrDiscover(appDirectory, explicitEntry);
        _logger.Info($"Carregando app {manifest.Name} v{manifest.Version} em {appDirectory}.");
        _packageManager.ValidateDependencies(manifest.Dependencies);

        var entry = _manifestLoader.ResolveEntry(appDirectory, manifest.Entry);
        var environment = new Dictionary<string, string>
        {
            ["VOLTPY_APP_NAME"] = manifest.Name,
            ["VOLTPY_APP_VERSION"] = manifest.Version,
            ["VOLTPY_APP_DIR"] = appDirectory,
            ["VOLTPY_APP_DEPENDENCIES"] = string.Join(';', manifest.Dependencies),
        };

        var result = await _runtimeHost.ExecuteScriptAsync(entry, environment, cancellationToken);
        return result.ExitCode;
    }

    private (string AppDirectory, string? ExplicitEntry) ResolveAppTarget(string? appPathOrEntry)
    {
        if (string.IsNullOrWhiteSpace(appPathOrEntry) || appPathOrEntry == ".")
        {
            return (_paths.AppDirectory, null);
        }

        var raw = Path.IsPathRooted(appPathOrEntry)
            ? appPathOrEntry
            : Path.Combine(_paths.AppDirectory, appPathOrEntry);
        var fullPath = Path.GetFullPath(raw);

        if (File.Exists(fullPath))
        {
            return (Path.GetDirectoryName(fullPath)!, Path.GetFileName(fullPath));
        }

        if (Directory.Exists(fullPath))
        {
            return (fullPath, null);
        }

        // Treat unknown simple values as an entrypoint under the app root so
        // App.py/main.py/teste.py discovery remains the default behavior.
        return (_paths.AppDirectory, appPathOrEntry);
    }
}
