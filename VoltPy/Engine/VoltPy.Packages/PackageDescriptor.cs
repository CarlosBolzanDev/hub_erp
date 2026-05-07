using System.Text.Json.Serialization;

namespace VoltPy.Packages;

public sealed record PackageDescriptor(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("version")] string Version,
    [property: JsonPropertyName("module")] string Module,
    [property: JsonPropertyName("enabled")] bool Enabled = true);
