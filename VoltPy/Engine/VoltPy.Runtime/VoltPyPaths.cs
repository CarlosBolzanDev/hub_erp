namespace VoltPy.Runtime;

/// <summary>
/// Centraliza os diretórios físicos da distribuição VoltPy para evitar hardcode
/// em loaders, apps e gerenciadores de pacote.
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
    string ConfigDirectory)
{
    public string PythonExecutable => Path.Combine(RuntimeDirectory, OperatingSystem.IsWindows() ? "python.exe" : "python");
    public string PythonHome => RuntimeDirectory;
    public string PythonLib => Path.Combine(RuntimeDirectory, "Lib");
    public string SitePackages => Path.Combine(RuntimeDirectory, "site-packages");
    public string BootstrapScript => Path.Combine(NamespaceDirectory, "bootstrap.py");

    public static VoltPyPaths Discover(string? startDirectory = null)
    {
        var current = new DirectoryInfo(startDirectory ?? AppContext.BaseDirectory);
        while (current is not null)
        {
            var candidate = Path.Combine(current.FullName, "VoltPy");
            if (Directory.Exists(candidate) && Directory.Exists(Path.Combine(candidate, "Runtime")))
            {
                return FromRoot(candidate);
            }
            current = current.Parent;
        }

        return FromRoot(Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "VoltPy")));
    }

    public static VoltPyPaths FromRoot(string rootDirectory)
    {
        var root = Path.GetFullPath(rootDirectory);
        return new VoltPyPaths(
            root,
            Path.Combine(root, "Engine"),
            Path.Combine(root, "Runtime"),
            Path.Combine(root, "Packages"),
            Path.Combine(root, "Apps"),
            Path.Combine(root, "VoltPy"),
            Path.Combine(root, "Logs"),
            Path.Combine(root, "Temp"),
            Path.Combine(root, "Config"));
    }

    public void EnsureBaseDirectories()
    {
        foreach (var path in new[] { EngineDirectory, RuntimeDirectory, PackagesDirectory, AppsDirectory, NamespaceDirectory, LogsDirectory, TempDirectory, ConfigDirectory })
        {
            Directory.CreateDirectory(path);
        }
    }
}
