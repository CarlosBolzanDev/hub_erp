using System.Text.Json.Serialization;

namespace VoltPy.Runtime;

/// <summary>
/// Configuração serializável para a engine portátil. Normalmente nenhum arquivo
/// é necessário: ao copiar a pasta VoltPy para dentro do app, a engine usa a
/// própria pasta como raiz e o diretório pai como AppDirectory.
/// </summary>
public sealed record VoltPyPathOptions
{
    [JsonPropertyName("EngineDirectory")]
    public string? EngineDirectory { get; init; }

    [JsonPropertyName("AppDirectory")]
    public string? AppDirectory { get; init; }

    [JsonPropertyName("NamespaceDirectory")]
    public string? NamespaceDirectory { get; init; }

    [JsonPropertyName("RuntimeDirectory")]
    public string? RuntimeDirectory { get; init; }

    [JsonPropertyName("PackagesDirectory")]
    public string? PackagesDirectory { get; init; }

    [JsonPropertyName("LogsDirectory")]
    public string? LogsDirectory { get; init; }

    [JsonPropertyName("TempDirectory")]
    public string? TempDirectory { get; init; }

    [JsonPropertyName("ConfigDirectory")]
    public string? ConfigDirectory { get; init; }

    [JsonPropertyName("PythonExecutable")]
    public string? PythonExecutable { get; init; }

    [JsonPropertyName("PythonHome")]
    public string? PythonHome { get; init; }

    [JsonPropertyName("UseSystemPythonFallback")]
    public bool? UseSystemPythonFallback { get; init; }

    [JsonPropertyName("AdditionalPythonPath")]
    public IReadOnlyList<string>? AdditionalPythonPath { get; init; }
}
