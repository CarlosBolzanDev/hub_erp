using System.Text.Json;

namespace VoltPy.Runtime;

public sealed record VoltPyHostConfiguration(VoltPyPaths Paths, PythonRuntimeOptions RuntimeOptions, string? SourceFile);

/// <summary>
/// Carrega a configuração externa do host sem assumir que o executável e o
/// runtime/namespace VoltPy estejam na mesma árvore física.
/// </summary>
public static class VoltPyConfigurationLoader
{
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web)
    {
        ReadCommentHandling = JsonCommentHandling.Skip,
        AllowTrailingCommas = true,
        PropertyNameCaseInsensitive = true,
    };

    public static VoltPyHostConfiguration Load(string? configFile, string? voltPyRootOverride, string hostBaseDirectory)
    {
        var resolvedConfigFile = ResolveConfigFile(configFile, hostBaseDirectory);
        var options = resolvedConfigFile is not null
            ? JsonSerializer.Deserialize<VoltPyPathOptions>(File.ReadAllText(resolvedConfigFile), JsonOptions) ?? new VoltPyPathOptions()
            : new VoltPyPathOptions();

        var envRoot = Environment.GetEnvironmentVariable("VOLTPY_ROOT");
        var root = FirstNonEmpty(voltPyRootOverride, envRoot, options.VoltPyRoot)
            ?? throw new InvalidOperationException("VoltPyRoot não foi informado. Use --voltpy-root, VOLTPY_ROOT ou config/host.json.");

        var rootBase = resolvedConfigFile is not null
            ? Path.GetDirectoryName(resolvedConfigFile)!
            : hostBaseDirectory;
        var paths = VoltPyPaths.FromOptions(options, root, rootBase);
        paths.EnsureBaseDirectories();

        var runtimeOptions = new PythonRuntimeOptions
        {
            HiddenWindow = true,
            UseSystemPythonFallback = options.UseSystemPythonFallback ?? false,
            AdditionalPythonPath = ResolveAdditionalPythonPath(options.AdditionalPythonPath, paths.RootDirectory),
        };

        return new VoltPyHostConfiguration(paths, runtimeOptions, resolvedConfigFile);
    }

    private static string? ResolveConfigFile(string? configFile, string hostBaseDirectory)
    {
        var envConfig = Environment.GetEnvironmentVariable("VOLTPY_HOST_CONFIG");
        foreach (var candidate in new[]
        {
            configFile,
            envConfig,
            Path.Combine(hostBaseDirectory, "config", "host.json"),
            Path.Combine(Environment.CurrentDirectory, "config", "host.json"),
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

    private static IReadOnlyList<string> ResolveAdditionalPythonPath(IReadOnlyList<string>? paths, string rootDirectory)
    {
        if (paths is null || paths.Count == 0)
        {
            return Array.Empty<string>();
        }

        return paths.Select(path => Path.GetFullPath(path, rootDirectory)).ToArray();
    }

    private static string? FirstNonEmpty(params string?[] values) => values.FirstOrDefault(value => !string.IsNullOrWhiteSpace(value));
}
