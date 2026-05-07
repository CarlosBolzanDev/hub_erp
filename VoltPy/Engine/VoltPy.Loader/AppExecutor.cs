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

    public async Task<int> ExecuteAsync(string appNameOrPath, CancellationToken cancellationToken = default)
    {
        var appDirectory = ResolveAppDirectory(appNameOrPath);
        var manifest = _manifestLoader.Load(appDirectory);
        _logger.Info($"Carregando app {manifest.Name} v{manifest.Version} em {appDirectory}.");
        _packageManager.ValidateDependencies(manifest.Dependencies);

        var entry = Path.GetFullPath(Path.Combine(appDirectory, manifest.Entry));
        var relativeEntry = Path.GetRelativePath(appDirectory, entry);
        if (relativeEntry.StartsWith("..", StringComparison.Ordinal) || Path.IsPathRooted(relativeEntry))
        {
            throw new InvalidOperationException("Entry do manifest não pode apontar para fora do diretório do app.");
        }

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

    private string ResolveAppDirectory(string appNameOrPath)
    {
        var path = Path.IsPathRooted(appNameOrPath)
            ? appNameOrPath
            : Path.Combine(_paths.AppsDirectory, appNameOrPath);

        path = Path.GetFullPath(path);
        if (!Directory.Exists(path))
        {
            throw new DirectoryNotFoundException($"App VoltPy não encontrado: {path}");
        }

        return path;
    }
}
