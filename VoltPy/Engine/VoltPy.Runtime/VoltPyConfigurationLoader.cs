using System.Text.Json;

namespace VoltPy.Runtime;

public sealed record VoltPyHostConfiguration(VoltPyPaths Paths, PythonRuntimeOptions RuntimeOptions, string? SourceFile);

/// <summary>
/// Carrega configuração opcional da engine portátil. Se nenhum arquivo/argumento
/// for informado, procura a pasta VoltPy no diretório atual ou acima dele.
/// </summary>
public static class VoltPyConfigurationLoader
{
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web)
    {
        ReadCommentHandling = JsonCommentHandling.Skip,
        AllowTrailingCommas = true,
        PropertyNameCaseInsensitive = true,
    };

    public static VoltPyHostConfiguration Load(string? configFile, string? engineOverride, string hostBaseDirectory)
    {
        var resolvedConfigFile = ResolveConfigFile(configFile, hostBaseDirectory);
        var options = resolvedConfigFile is not null
            ? JsonSerializer.Deserialize<VoltPyPathOptions>(File.ReadAllText(resolvedConfigFile), JsonOptions) ?? new VoltPyPathOptions()
            : new VoltPyPathOptions();

        var envEngine = Environment.GetEnvironmentVariable("VOLTPY_ENGINE_DIR");
        var engine = FirstNonEmpty(engineOverride, envEngine, options.EngineDirectory)
            ?? DiscoverEngineDirectory(hostBaseDirectory)
            ?? throw new InvalidOperationException("Pasta da engine VoltPy não encontrada. Copie VoltPy para dentro do app ou use --engine-dir.");

        var rootBase = resolvedConfigFile is not null
            ? Path.GetDirectoryName(resolvedConfigFile)!
            : hostBaseDirectory;
        var paths = VoltPyPaths.FromOptions(options, engine, rootBase);
        paths.EnsureBaseDirectories();

        var runtimeOptions = new PythonRuntimeOptions
        {
            HiddenWindow = true,
            UseSystemPythonFallback = options.UseSystemPythonFallback ?? false,
            AdditionalPythonPath = ResolveAdditionalPythonPath(options.AdditionalPythonPath, paths.EngineDirectory),
        };

        return new VoltPyHostConfiguration(paths, runtimeOptions, resolvedConfigFile);
    }

    private static string? ResolveConfigFile(string? configFile, string hostBaseDirectory)
    {
        var envConfig = Environment.GetEnvironmentVariable("VOLTPY_CONFIG");
        foreach (var candidate in new[]
        {
            configFile,
            envConfig,
            Path.Combine(hostBaseDirectory, "VoltPy", "config", "runtime.json"),
            Path.Combine(Environment.CurrentDirectory, "VoltPy", "config", "runtime.json"),
        })
        {
            if (string.IsNullOrWhiteSpace(candidate))
            {
                continue;
            }

            var fullPath = Path.GetFullPath(candidate, hostBaseDirectory);
            if (File.Exists(fullPath))
            {
                return fullPath;
            }
        }

        return null;
    }

    private static string? DiscoverEngineDirectory(string startDirectory)
    {
        var current = new DirectoryInfo(Environment.CurrentDirectory);
        while (current is not null)
        {
            var candidate = Path.Combine(current.FullName, "VoltPy");
            if (Directory.Exists(candidate) && Directory.Exists(Path.Combine(candidate, "voltpy")))
            {
                return candidate;
            }
            current = current.Parent;
        }

        var hostCandidate = Path.Combine(startDirectory, "VoltPy");
        return Directory.Exists(Path.Combine(hostCandidate, "voltpy")) ? hostCandidate : null;
    }

    private static IReadOnlyList<string> ResolveAdditionalPythonPath(IReadOnlyList<string>? paths, string engineDirectory)
    {
        if (paths is null || paths.Count == 0)
        {
            return Array.Empty<string>();
        }

        return paths.Select(path => Path.GetFullPath(path, engineDirectory)).ToArray();
    }

    private static string? FirstNonEmpty(params string?[] values) => values.FirstOrDefault(value => !string.IsNullOrWhiteSpace(value));
}
