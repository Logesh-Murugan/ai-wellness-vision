// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'analysis_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$analysisHistoryHash() => r'c0473b06d097999864db7e1dc8baf693ca6d3377';

/// Copied from Dart SDK
class _SystemHash {
  _SystemHash._();

  static int combine(int hash, int value) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + value);
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x0007ffff & hash) << 10));
    return hash ^ (hash >> 6);
  }

  static int finish(int hash) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x03ffffff & hash) << 3));
    // ignore: parameter_assignments
    hash = hash ^ (hash >> 11);
    return 0x1fffffff & (hash + ((0x00003fff & hash) << 15));
  }
}

/// See also [analysisHistory].
@ProviderFor(analysisHistory)
const analysisHistoryProvider = AnalysisHistoryFamily();

/// See also [analysisHistory].
class AnalysisHistoryFamily extends Family<AsyncValue<List<AnalysisRecord>>> {
  /// See also [analysisHistory].
  const AnalysisHistoryFamily();

  /// See also [analysisHistory].
  AnalysisHistoryProvider call({
    int limit = 10,
    int offset = 0,
  }) {
    return AnalysisHistoryProvider(
      limit: limit,
      offset: offset,
    );
  }

  @override
  AnalysisHistoryProvider getProviderOverride(
    covariant AnalysisHistoryProvider provider,
  ) {
    return call(
      limit: provider.limit,
      offset: provider.offset,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'analysisHistoryProvider';
}

/// See also [analysisHistory].
class AnalysisHistoryProvider
    extends AutoDisposeFutureProvider<List<AnalysisRecord>> {
  /// See also [analysisHistory].
  AnalysisHistoryProvider({
    int limit = 10,
    int offset = 0,
  }) : this._internal(
          (ref) => analysisHistory(
            ref as AnalysisHistoryRef,
            limit: limit,
            offset: offset,
          ),
          from: analysisHistoryProvider,
          name: r'analysisHistoryProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$analysisHistoryHash,
          dependencies: AnalysisHistoryFamily._dependencies,
          allTransitiveDependencies:
              AnalysisHistoryFamily._allTransitiveDependencies,
          limit: limit,
          offset: offset,
        );

  AnalysisHistoryProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.limit,
    required this.offset,
  }) : super.internal();

  final int limit;
  final int offset;

  @override
  Override overrideWith(
    FutureOr<List<AnalysisRecord>> Function(AnalysisHistoryRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: AnalysisHistoryProvider._internal(
        (ref) => create(ref as AnalysisHistoryRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        limit: limit,
        offset: offset,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<List<AnalysisRecord>> createElement() {
    return _AnalysisHistoryProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is AnalysisHistoryProvider &&
        other.limit == limit &&
        other.offset == offset;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, limit.hashCode);
    hash = _SystemHash.combine(hash, offset.hashCode);

    return _SystemHash.finish(hash);
  }
}

mixin AnalysisHistoryRef on AutoDisposeFutureProviderRef<List<AnalysisRecord>> {
  /// The parameter `limit` of this provider.
  int get limit;

  /// The parameter `offset` of this provider.
  int get offset;
}

class _AnalysisHistoryProviderElement
    extends AutoDisposeFutureProviderElement<List<AnalysisRecord>>
    with AnalysisHistoryRef {
  _AnalysisHistoryProviderElement(super.provider);

  @override
  int get limit => (origin as AnalysisHistoryProvider).limit;
  @override
  int get offset => (origin as AnalysisHistoryProvider).offset;
}

String _$imageAnalysisNotifierHash() =>
    r'6b14ca875db77a541ab40fa173c7a9c8eb9c6635';

/// See also [ImageAnalysisNotifier].
@ProviderFor(ImageAnalysisNotifier)
final imageAnalysisNotifierProvider = AutoDisposeAsyncNotifierProvider<
    ImageAnalysisNotifier, AnalysisResult?>.internal(
  ImageAnalysisNotifier.new,
  name: r'imageAnalysisNotifierProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$imageAnalysisNotifierHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$ImageAnalysisNotifier = AutoDisposeAsyncNotifier<AnalysisResult?>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member
