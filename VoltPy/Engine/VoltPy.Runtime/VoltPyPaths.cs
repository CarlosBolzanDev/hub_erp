namespace VoltPy.Runtime;

/// <summary>
/// Representa todos os caminhos físicos da instalação externa VoltPy. A classe
/// não descobre caminhos a partir do executável do host; ela normaliza valores
/// vindos de arquivo de configuração, variáveis de ambiente ou argumentos CLI.
/// </summary>
public sealed record VoltPyPaths(
    string RootDirectory,
    string EngineDirectory,
    string RuntimeDirectory,
    string PackagesDirectory,
    string AppsDirectory,
    string NamespaceDirectory,
    string LogsDirectory,
    string TempDirectory,
    string ConfigDirectory,
    string PythonExecutablePath,
    string PythonHomeDirectory)
{
    public string PythonExecutable => PythonExecutablePath;
    public string PythonHome => PythonHomeDirectory;
    public string PythonLib => Path.Combine(RuntimeDirectory, "Lib");
    public string SitePackages => Path.Combine(RuntimeDirectory, "site-packages");
    public string BootstrapScript => Path.Combine(NamespaceDirectory, "bootstrap.py");

    public static VoltPyPaths FromOptions(VoltPyPathOptions options, string rootDirectory, string rootBaseDirectory)
    {
        var root = ResolveRoot(rootDirectory, rootBaseDirectory);
        var runtimeDirectory = ResolvePath(options.RuntimeDirectory, root, "Runtime");

        return new VoltPyPaths(
            root,
            ResolvePath(options.EngineDirectory, root, "Engine"),
            runtimeDirectory,
            ResolvePath(options.PackagesDirectory, root, "Packages"),
            ResolvePath(options.AppsDirectory, root, "Apps"),
            ResolvePath(options.NamespaceDirectory, root, "VoltPy"),
            ResolvePath(options.LogsDirectory, root, "Logs"),
            ResolvePath(options.TempDirectory, root, "Temp"),
            ResolvePath(options.ConfigDirectory, root, "Config"),
            ResolvePath(options.PythonExecutable, runtimeDirectory, OperatingSystem.IsWindows() ? "python.exe" : "python"),
            ResolvePath(options.PythonHome, runtimeDirectory, "."));
    }

    public void EnsureBaseDirectories()
    {
        foreach (var path in new[] { EngineDirectory, RuntimeDirectory, PackagesDirectory, AppsDirectory, NamespaceDirectory, LogsDirectory, TempDirectory, ConfigDirectory, SitePackages, PythonLib })
        {
            Directory.CreateDirectory(path);
        }
    }

    private static string ResolveRoot(string path, string rootBaseDirectory)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            throw new ArgumentException("VoltPyRoot não pode ser vazio.", nameof(path));
        }

        return Path.GetFullPath(path, rootBaseDirectory);
    }

    private static string ResolvePath(string? configuredPath, string baseDirectory, string defaultRelativePath)
    {
        var selected = string.IsNullOrWhiteSpace(configuredPath) ? defaultRelativePath : configuredPath;
        return Path.GetFullPath(selected!, baseDirectory);
    }
}
