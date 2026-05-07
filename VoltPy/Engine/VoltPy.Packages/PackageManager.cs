using System.Text.Json;
using VoltPy.Runtime;

namespace VoltPy.Packages;

public interface IPackageManager
{
    IReadOnlyCollection<PackageDescriptor> GetInstalledPackages();
    void ValidateDependencies(IEnumerable<string> dependencies);
}

/// <summary>
/// Gerenciador interno preparado para comandos futuros como `voltpy install pandas`.
/// Na versão inicial ele valida a presença dos diretórios de pacote gerenciados.
/// </summary>
public sealed class PackageManager : IPackageManager
{
    private readonly VoltPyPaths _paths;
    private readonly IVoltPyLogger _logger;
    private readonly JsonSerializerOptions _json = new(JsonSerializerDefaults.Web);

    public PackageManager(VoltPyPaths paths, IVoltPyLogger logger)
    {
        _paths = paths;
        _logger = logger;
    }

    public IReadOnlyCollection<PackageDescriptor> GetInstalledPackages()
    {
        if (!Directory.Exists(_paths.PackagesDirectory))
        {
            return Array.Empty<PackageDescriptor>();
        }

        return Directory.EnumerateDirectories(_paths.PackagesDirectory)
            .Select(CreateDescriptor)
            .Where(package => package.Enabled)
            .OrderBy(package => package.Name, StringComparer.OrdinalIgnoreCase)
            .ToArray();
    }

    public void ValidateDependencies(IEnumerable<string> dependencies)
    {
        var installed = GetInstalledPackages().Select(package => package.Name).ToHashSet(StringComparer.OrdinalIgnoreCase);
        var missing = dependencies.Where(dependency => !installed.Contains(dependency)).Distinct(StringComparer.OrdinalIgnoreCase).ToArray();
        if (missing.Length > 0)
        {
            throw new InvalidOperationException($"Dependências ausentes no runtime VoltPy: {string.Join(", ", missing)}");
        }

        _logger.Info($"Dependências validadas: {string.Join(", ", dependencies)}");
    }

    private PackageDescriptor CreateDescriptor(string directory)
    {
        var manifest = Path.Combine(directory, "voltpy-package.json");
        if (File.Exists(manifest))
        {
            var parsed = JsonSerializer.Deserialize<PackageDescriptor>(File.ReadAllText(manifest), _json);
            if (parsed is not null)
            {
                return parsed;
            }
        }

        var name = Path.GetFileName(directory);
        return new PackageDescriptor(name, "0.0.0", name);
    }
}
