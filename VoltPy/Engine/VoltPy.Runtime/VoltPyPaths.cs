namespace VoltPy.Runtime;

/// <summary>
/// Caminhos físicos de uma engine VoltPy copiada para dentro de um app.
/// EngineDirectory é a pasta VoltPy; AppDirectory é o diretório pai do app.
/// </summary>
public sealed record VoltPyPaths(
    string EngineDirectory,
    string AppDirectory,
    string RuntimeDirectory,
    string PackagesDirectory,
    string NamespaceDirectory,
    string LogsDirectory,
    string TempDirectory,
    string ConfigDirectory,
    string PythonExecutablePath,
    string PythonHomeDirectory)
{
    public string RootDirectory => EngineDirectory;
    public string PythonExecutable => PythonExecutablePath;
    public string PythonHome => PythonHomeDirectory;
    public string PythonLib => Path.Combine(RuntimeDirectory, "Lib");
    public string SitePackages => Path.Combine(RuntimeDirectory, "site-packages");
    public string BootstrapScript => Path.Combine(NamespaceDirectory, "bootstrap.py");

    public static VoltPyPaths FromOptions(VoltPyPathOptions options, string engineDirectory, string engineBaseDirectory)
    {
        var engine = ResolveRoot(engineDirectory, engineBaseDirectory);
        var appDirectory = ResolvePath(options.AppDirectory, Directory.GetParent(engine)?.FullName ?? engine, ".");
        var runtimeDirectory = ResolvePath(options.RuntimeDirectory, engine, "runtime");

        return new VoltPyPaths(
            engine,
            appDirectory,
            runtimeDirectory,
            ResolvePath(options.PackagesDirectory, engine, "packages"),
            ResolvePath(options.NamespaceDirectory, engine, "voltpy"),
            ResolvePath(options.LogsDirectory, engine, "logs"),
            ResolvePath(options.TempDirectory, engine, "temp"),
            ResolvePath(options.ConfigDirectory, engine, "config"),
            ResolvePath(options.PythonExecutable, runtimeDirectory, OperatingSystem.IsWindows() ? "python.exe" : "python"),
            ResolvePath(options.PythonHome, runtimeDirectory, "."));
    }

    public void EnsureBaseDirectories()
    {
        foreach (var path in new[] { RuntimeDirectory, PackagesDirectory, NamespaceDirectory, LogsDirectory, TempDirectory, ConfigDirectory, SitePackages, PythonLib })
        {
            Directory.CreateDirectory(path);
        }
    }

    private static string ResolveRoot(string path, string rootBaseDirectory)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            throw new ArgumentException("EngineDirectory não pode ser vazio.", nameof(path));
        }

        return Path.GetFullPath(path, rootBaseDirectory);
    }

    private static string ResolvePath(string? configuredPath, string baseDirectory, string defaultRelativePath)
    {
        var selected = string.IsNullOrWhiteSpace(configuredPath) ? defaultRelativePath : configuredPath;
        return Path.GetFullPath(selected!, baseDirectory);
    }
}
