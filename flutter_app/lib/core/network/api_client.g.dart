// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'api_client.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$secureStorageHash() => r'77df30c7098a9f252222741225993ef719fafe36';

/// See also [secureStorage].
@ProviderFor(secureStorage)
final secureStorageProvider =
    AutoDisposeProvider<FlutterSecureStorage>.internal(
  secureStorage,
  name: r'secureStorageProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$secureStorageHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef SecureStorageRef = AutoDisposeProviderRef<FlutterSecureStorage>;
String _$apiClientHash() => r'0f143ae24b2762406ec2ffedbca0eb71af2250aa';

/// See also [apiClient].
@ProviderFor(apiClient)
final apiClientProvider = AutoDisposeProvider<Dio>.internal(
  apiClient,
  name: r'apiClientProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$apiClientHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef ApiClientRef = AutoDisposeProviderRef<Dio>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member
