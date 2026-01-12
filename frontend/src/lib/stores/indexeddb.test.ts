/**
 * Tests for IndexedDB storage manager.
 *
 * These tests validate the IndexedDBManager functionality including
 * database initialization, CRUD operations, and error handling.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
	IndexedDBManager,
	DATABASE_NAME,
	DATABASE_VERSION,
	STORE_TRANSLATIONS,
	STORE_HISTORY,
	STORE_NOTES,
	STORE_ARTIFACTS,
	QuotaExceededError,
	DatabaseError,
	type TranslationRecord,
	type HistoryEntry
} from './indexeddb';

// Mock IndexedDB
class MockIDBDatabase {
	name: string;
	version: number;
	objectStoreNames: DOMStringList;
	private stores: Map<string, MockIDBObjectStore>;

	constructor(name: string, version: number) {
		this.name = name;
		this.version = version;
		this.stores = new Map();
		this.objectStoreNames = {
			contains: (name: string) => this.stores.has(name),
			item: (index: number) => Array.from(this.stores.keys())[index] || null,
			length: this.stores.size
		} as DOMStringList;
	}

	createObjectStore(name: string, options: IDBObjectStoreParameters): MockIDBObjectStore {
		const store = new MockIDBObjectStore(name, options);
		this.stores.set(name, store);
		return store;
	}

	transaction(
		storeNames: string | string[],
		mode: IDBTransactionMode = 'readonly'
	): MockIDBTransaction {
		return new MockIDBTransaction(this.stores, storeNames, mode);
	}

	close(): void {
		// Mock close
	}
}

class MockIDBObjectStore {
	name: string;
	keyPath: string | string[];
	private data: Map<string, unknown>;
	private indexes: Map<string, MockIDBIndex>;

	constructor(name: string, options: IDBObjectStoreParameters) {
		this.name = name;
		this.keyPath = options.keyPath as string | string[];
		this.data = new Map();
		this.indexes = new Map();
	}

	createIndex(
		name: string,
		keyPath: string | string[],
		options?: IDBIndexParameters
	): MockIDBIndex {
		const index = new MockIDBIndex(name, keyPath, this.data, options);
		this.indexes.set(name, index);
		return index;
	}

	add(value: unknown): MockIDBRequest {
		const request = new MockIDBRequest();
		setTimeout(() => {
			try {
				const key = (value as Record<string, string>)[this.keyPath as string];
				if (this.data.has(key)) {
					request._setError(new Error('Key already exists'));
				} else {
					this.data.set(key, value);
					request._setResult(key);
				}
			} catch (error) {
				request._setError(error as Error);
			}
		}, 0);
		return request;
	}

	delete(key: string): MockIDBRequest {
		const request = new MockIDBRequest();
		setTimeout(() => {
			this.data.delete(key);
			request._setResult(undefined);
		}, 0);
		return request;
	}

	index(name: string): MockIDBIndex {
		const index = this.indexes.get(name);
		if (!index) {
			throw new Error(`Index ${name} not found`);
		}
		return index;
	}
}

class MockIDBIndex {
	name: string;
	keyPath: string | string[];
	private data: Map<string, unknown>;

	constructor(
		name: string,
		keyPath: string | string[],
		data: Map<string, unknown>,
		// eslint-disable-next-line @typescript-eslint/no-unused-vars
		__options?: IDBIndexParameters
	) {
		this.name = name;
		this.keyPath = keyPath;
		this.data = data;
	}

	getAll(query?: string): MockIDBRequest {
		const request = new MockIDBRequest();
		setTimeout(() => {
			const results = Array.from(this.data.values()).filter((item) => {
				if (!query) return true;
				return (item as Record<string, string>)[this.keyPath as string] === query;
			});
			request._setResult(results);
		}, 0);
		return request;
	}

	openCursor(range?: IDBKeyRange): MockIDBRequest {
		const request = new MockIDBRequest();
		setTimeout(() => {
			const items = Array.from(this.data.entries());
			let currentIndex = 0;

			const cursor = {
				value: items[currentIndex]?.[1],
				continue: () => {
					currentIndex++;
					if (currentIndex < items.length) {
						// Filter by range if provided
						const item = items[currentIndex][1] as Record<string, number>;
						const keyValue = item[this.keyPath as string];

						if (range && typeof range.upper === 'number' && keyValue > range.upper) {
							request._setResult(null);
							return;
						}

						setTimeout(() => {
							request._setResult({
								value: items[currentIndex][1],
								delete: () => {
									this.data.delete(items[currentIndex][0]);
									return new MockIDBRequest();
								},
								continue: cursor.continue
							});
						}, 0);
					} else {
						request._setResult(null);
					}
				},
				delete: () => {
					this.data.delete(items[currentIndex][0]);
					return new MockIDBRequest();
				}
			};

			if (items.length > 0) {
				// Filter first item by range
				const item = items[0][1] as Record<string, number>;
				const keyValue = item[this.keyPath as string];

				if (range && typeof range.upper === 'number' && keyValue > range.upper) {
					request._setResult(null);
					return;
				}

				request._setResult(cursor);
			} else {
				request._setResult(null);
			}
		}, 0);
		return request;
	}
}

class MockIDBTransaction {
	error: Error | null = null;
	private stores: Map<string, MockIDBObjectStore>;

	constructor(
		stores: Map<string, MockIDBObjectStore>,
		// eslint-disable-next-line @typescript-eslint/no-unused-vars
		__storeNames: string | string[],
		// eslint-disable-next-line @typescript-eslint/no-unused-vars
		__mode: IDBTransactionMode
	) {
		this.stores = stores;
	}

	objectStore(name: string): MockIDBObjectStore {
		const store = this.stores.get(name);
		if (!store) {
			throw new Error(`Object store ${name} not found`);
		}
		return store;
	}
}

class MockIDBRequest {
	result: unknown = null;
	error: Error | null = null;
	onsuccess: ((event: Event) => void) | null = null;
	onerror: ((event: Event) => void) | null = null;

	_setResult(value: unknown): void {
		this.result = value;
		if (this.onsuccess) {
			this.onsuccess({ target: this } as unknown as Event);
		}
	}

	_setError(error: Error): void {
		this.error = error;
		if (this.onerror) {
			this.onerror({ target: this } as unknown as Event);
		}
	}
}

class MockIDBOpenDBRequest extends MockIDBRequest {
	onupgradeneeded: ((event: IDBVersionChangeEvent) => void) | null = null;

	_triggerUpgrade(oldVersion: number, newVersion: number, db: MockIDBDatabase): void {
		if (this.onupgradeneeded) {
			this.onupgradeneeded({
				oldVersion,
				newVersion,
				target: { result: db }
			} as unknown as IDBVersionChangeEvent);
		}
	}
}

describe('IndexedDB Manager', () => {
	let manager: IndexedDBManager;
	let mockDB: MockIDBDatabase;

	beforeEach(() => {
		// Setup IndexedDB mock
		mockDB = new MockIDBDatabase(DATABASE_NAME, DATABASE_VERSION);

		global.indexedDB = {
			open: (name: string, version: number) => {
				const request = new MockIDBOpenDBRequest();
				setTimeout(() => {
					// Trigger upgrade for new database
					request._triggerUpgrade(0, version, mockDB);
					request._setResult(mockDB);
				}, 0);
				return request as unknown as IDBOpenDBRequest;
			}
		} as IDBFactory;

		// Mock IDBKeyRange
		global.IDBKeyRange = {
			upperBound: (upper: number) => ({ upper })
		} as unknown as typeof IDBKeyRange;

		manager = new IndexedDBManager();
	});

	afterEach(() => {
		manager.close();
	});

	describe('Database Initialization', () => {
		it('should create database with correct name and version', async () => {
			const db = await manager.getDB();
			expect(db.name).toBe(DATABASE_NAME);
			expect(db.version).toBe(DATABASE_VERSION);
		});

		it('should create all required object stores', async () => {
			const db = await manager.getDB();
			expect(db.objectStoreNames.contains(STORE_TRANSLATIONS)).toBe(true);
			expect(db.objectStoreNames.contains(STORE_HISTORY)).toBe(true);
			expect(db.objectStoreNames.contains(STORE_NOTES)).toBe(true);
			expect(db.objectStoreNames.contains(STORE_ARTIFACTS)).toBe(true);
		});

		it('should return same database instance on multiple calls', async () => {
			const db1 = await manager.getDB();
			const db2 = await manager.getDB();
			expect(db1).toBe(db2);
		});
	});

	describe('Translation Operations', () => {
		it('should add a translation record', async () => {
			const translation: TranslationRecord = {
				translation_id: 'trans-123',
				document_url: 'https://example.com',
				block_id: 'block-1',
				source_text: 'Hello',
				translated_text: 'Hola',
				source_language: 'en',
				target_language: 'es',
				provider: 'openai',
				model: 'gpt-4',
				created_at: Date.now()
			};

			await expect(manager.addTranslation(translation)).resolves.toBeUndefined();
		});

		it('should get translations by document URL', async () => {
			const translation: TranslationRecord = {
				translation_id: 'trans-123',
				document_url: 'https://example.com',
				block_id: 'block-1',
				source_text: 'Hello',
				translated_text: 'Hola',
				source_language: 'en',
				target_language: 'es',
				provider: 'openai',
				model: 'gpt-4',
				created_at: Date.now()
			};

			await manager.addTranslation(translation);
			const translations = await manager.getTranslations('https://example.com');

			expect(translations).toHaveLength(1);
			expect(translations[0].translation_id).toBe('trans-123');
		});

		it('should delete a translation by ID', async () => {
			const translation: TranslationRecord = {
				translation_id: 'trans-123',
				document_url: 'https://example.com',
				block_id: 'block-1',
				source_text: 'Hello',
				translated_text: 'Hola',
				source_language: 'en',
				target_language: 'es',
				provider: 'openai',
				model: 'gpt-4',
				created_at: Date.now()
			};

			await manager.addTranslation(translation);
			await manager.deleteTranslation('trans-123');

			const translations = await manager.getTranslations('https://example.com');
			expect(translations).toHaveLength(0);
		});
	});

	describe('History Operations', () => {
		it('should add a history entry', async () => {
			const entry: HistoryEntry = {
				history_id: 'hist-123',
				document_url: 'https://example.com',
				title: 'Example Page',
				visited_at: Date.now(),
				language_pair: 'en|es',
				content_preview: 'Preview text',
				metadata: { key: 'value' }
			};

			await expect(manager.addHistory(entry)).resolves.toBeUndefined();
		});

		it('should get history by document URL', async () => {
			const entry: HistoryEntry = {
				history_id: 'hist-123',
				document_url: 'https://example.com',
				title: 'Example Page',
				visited_at: Date.now(),
				language_pair: 'en|es',
				content_preview: 'Preview text',
				metadata: {}
			};

			await manager.addHistory(entry);
			const history = await manager.getHistory('https://example.com');

			expect(history).toHaveLength(1);
			expect(history[0].history_id).toBe('hist-123');
		});

		it('should clear old history entries', async () => {
			const now = Date.now();
			const oldEntry: HistoryEntry = {
				history_id: 'hist-old',
				document_url: 'https://old.com',
				title: 'Old Page',
				visited_at: now - 40 * 24 * 60 * 60 * 1000, // 40 days ago
				language_pair: 'en|es',
				content_preview: 'Old preview',
				metadata: {}
			};

			const recentEntry: HistoryEntry = {
				history_id: 'hist-recent',
				document_url: 'https://recent.com',
				title: 'Recent Page',
				visited_at: now - 10 * 24 * 60 * 60 * 1000, // 10 days ago
				language_pair: 'en|es',
				content_preview: 'Recent preview',
				metadata: {}
			};

			await manager.addHistory(oldEntry);
			await manager.addHistory(recentEntry);

			const deletedCount = await manager.clearOldHistory(30);
			expect(deletedCount).toBe(1);
		});
	});

	describe('Error Handling', () => {
		it('should handle database initialization error', async () => {
			// Close existing manager
			manager.close();

			// Create a manager that will fail
			const errorManager = new IndexedDBManager();

			// Mock indexedDB.open to fail
			global.indexedDB = {
				open: () => {
					const request = new MockIDBOpenDBRequest();
					setTimeout(() => {
						request._setError(new Error('DB open failed'));
					}, 0);
					return request as unknown as IDBOpenDBRequest;
				}
			} as unknown as IDBFactory;

			await expect(errorManager.getDB()).rejects.toThrow(DatabaseError);
		});

		it('should handle add translation error', async () => {
			// Get DB first
			await manager.getDB();

			// Mock transaction to fail
			const originalTransaction = mockDB.transaction;
			mockDB.transaction = vi.fn(() => {
				throw new Error('Transaction failed');
			});

			const translation: TranslationRecord = {
				translation_id: 'trans-123',
				document_url: 'https://example.com',
				block_id: 'block-1',
				source_text: 'Hello',
				translated_text: 'Hola',
				source_language: 'en',
				target_language: 'es',
				provider: 'openai',
				model: 'gpt-4',
				created_at: Date.now()
			};

			await expect(manager.addTranslation(translation)).rejects.toThrow(DatabaseError);

			// Restore
			mockDB.transaction = originalTransaction;
		});

		it('should handle get history error when operation fails', async () => {
			// Get DB first
			await manager.getDB();

			// Mock transaction to return a failing request
			const originalTransaction = mockDB.transaction;
			mockDB.transaction = vi.fn((storeNames: string | string[], mode: IDBTransactionMode) => {
				const transaction = originalTransaction.call(mockDB, storeNames, mode);
				const originalObjectStore = transaction.objectStore.bind(transaction);
				transaction.objectStore = vi.fn((name: string) => {
					const store = originalObjectStore(name);
					const originalIndex = store.index.bind(store);
					store.index = vi.fn((indexName: string) => {
						const index = originalIndex(indexName);
						// Use originalGetAll in the mock
						index.getAll = vi.fn(() => {
							const request = new MockIDBRequest();
							setTimeout(() => {
								request._setError(new Error('GetAll failed'));
							}, 0);
							return request;
						});
						return index;
					});
					return store;
				});
				return transaction;
			});

			await expect(manager.getHistory('https://example.com')).rejects.toThrow(DatabaseError);

			// Restore
			mockDB.transaction = originalTransaction;
		});

		it('should handle get history error when transaction fails', async () => {
			// Get DB first
			await manager.getDB();

			// Mock transaction to fail
			const originalTransaction = mockDB.transaction;
			mockDB.transaction = vi.fn(() => {
				throw new Error('Transaction failed');
			});

			await expect(manager.getHistory('https://example.com')).rejects.toThrow(DatabaseError);

			// Restore
			mockDB.transaction = originalTransaction;
		});

		it('should handle add history error when transaction fails', async () => {
			// Get DB first
			await manager.getDB();

			// Mock transaction to fail
			const originalTransaction = mockDB.transaction;
			mockDB.transaction = vi.fn(() => {
				throw new Error('Transaction failed');
			});

			const entry: HistoryEntry = {
				history_id: 'hist-error',
				document_url: 'https://example.com',
				title: 'Test',
				visited_at: Date.now(),
				language_pair: 'en|es',
				content_preview: 'Test',
				metadata: {}
			};

			await expect(manager.addHistory(entry)).rejects.toThrow(DatabaseError);

			// Restore
			mockDB.transaction = originalTransaction;
		});

		it('should handle quota exceeded error when adding history', async () => {
			// Get DB first
			await manager.getDB();

			// Mock transaction to return quota exceeded error
			const originalTransaction = mockDB.transaction;
			mockDB.transaction = vi.fn((storeNames: string | string[], mode: IDBTransactionMode) => {
				const transaction = originalTransaction.call(mockDB, storeNames, mode);
				const originalObjectStore = transaction.objectStore.bind(transaction);
				transaction.objectStore = vi.fn((name: string) => {
					const store = originalObjectStore(name);
					// Use originalAdd in the mock
					store.add = vi.fn(() => {
						const request = new MockIDBRequest();
						setTimeout(() => {
							const error = new Error('QuotaExceededError');
							error.name = 'QuotaExceededError';
							request._setError(error);
						}, 0);
						return request;
					});
					return store;
				});
				return transaction;
			});

			const entry: HistoryEntry = {
				history_id: 'hist-quota',
				document_url: 'https://example.com',
				title: 'Test',
				visited_at: Date.now(),
				language_pair: 'en|es',
				content_preview: 'Test',
				metadata: {}
			};

			await expect(manager.addHistory(entry)).rejects.toThrow(QuotaExceededError);

			// Restore
			mockDB.transaction = originalTransaction;
		});

		it('should handle add history request error (non-quota)', async () => {
			// Get DB first
			await manager.getDB();

			// Mock transaction to return regular error
			const originalTransaction = mockDB.transaction;
			mockDB.transaction = vi.fn((storeNames: string | string[], mode: IDBTransactionMode) => {
				const transaction = originalTransaction.call(mockDB, storeNames, mode);
				const originalObjectStore = transaction.objectStore.bind(transaction);
				transaction.objectStore = vi.fn((name: string) => {
					const store = originalObjectStore(name);
					// Use originalAdd in the mock
					store.add = vi.fn(() => {
						const request = new MockIDBRequest();
						setTimeout(() => {
							const error = new Error('Regular error');
							error.name = 'ConstraintError';
							request._setError(error);
						}, 0);
						return request;
					});
					return store;
				});
				return transaction;
			});

			const entry: HistoryEntry = {
				history_id: 'hist-error',
				document_url: 'https://example.com',
				title: 'Test',
				visited_at: Date.now(),
				language_pair: 'en|es',
				content_preview: 'Test',
				metadata: {}
			};

			await expect(manager.addHistory(entry)).rejects.toThrow(DatabaseError);

			// Restore
			mockDB.transaction = originalTransaction;
		});

		it('should handle clearOldHistory error when transaction fails', async () => {
			// Get DB first
			await manager.getDB();

			// Mock transaction to fail
			const originalTransaction = mockDB.transaction;
			mockDB.transaction = vi.fn(() => {
				throw new Error('Transaction failed');
			});

			await expect(manager.clearOldHistory(30)).rejects.toThrow(DatabaseError);

			// Restore
			mockDB.transaction = originalTransaction;
		});

		it('should handle clearOldHistory error when cursor operation fails', async () => {
			// Get DB first
			await manager.getDB();

			// Add an entry
			const entry: HistoryEntry = {
				history_id: 'hist-error',
				document_url: 'https://error.com',
				title: 'Error Page',
				visited_at: Date.now() - 40 * 24 * 60 * 60 * 1000,
				language_pair: 'en|es',
				content_preview: 'Error preview',
				metadata: {}
			};

			await manager.addHistory(entry);

			// Mock transaction to return a failing cursor request
			const originalTransaction = mockDB.transaction;
			mockDB.transaction = vi.fn((storeNames: string | string[], mode: IDBTransactionMode) => {
				const transaction = originalTransaction.call(mockDB, storeNames, mode);
				const originalObjectStore = transaction.objectStore.bind(transaction);
				transaction.objectStore = vi.fn((name: string) => {
					const store = originalObjectStore(name);
					const originalIndex = store.index.bind(store);
					store.index = vi.fn((indexName: string) => {
						const index = originalIndex(indexName);
						// Use originalOpenCursor in the mock
						index.openCursor = vi.fn(() => {
							const request = new MockIDBRequest();
							setTimeout(() => {
								request._setError(new Error('Cursor failed'));
							}, 0);
							return request;
						});
						return index;
					});
					return store;
				});
				return transaction;
			});

			await expect(manager.clearOldHistory(30)).rejects.toThrow(DatabaseError);

			// Restore
			mockDB.transaction = originalTransaction;
		});
	});

	describe('Integration Tests', () => {
		it('should complete full create-read-delete workflow for translations', async () => {
			// Create
			const translation: TranslationRecord = {
				translation_id: 'trans-workflow',
				document_url: 'https://workflow.com',
				block_id: 'block-1',
				source_text: 'Test',
				translated_text: 'Prueba',
				source_language: 'en',
				target_language: 'es',
				provider: 'openai',
				model: 'gpt-4',
				created_at: Date.now()
			};

			await manager.addTranslation(translation);

			// Read
			let translations = await manager.getTranslations('https://workflow.com');
			expect(translations).toHaveLength(1);
			expect(translations[0].source_text).toBe('Test');

			// Delete
			await manager.deleteTranslation('trans-workflow');

			// Verify deleted
			translations = await manager.getTranslations('https://workflow.com');
			expect(translations).toHaveLength(0);
		});

		it('should handle multiple translations for same document', async () => {
			const translation1: TranslationRecord = {
				translation_id: 'trans-1',
				document_url: 'https://multi.com',
				block_id: 'block-1',
				source_text: 'Hello',
				translated_text: 'Hola',
				source_language: 'en',
				target_language: 'es',
				provider: 'openai',
				model: 'gpt-4',
				created_at: Date.now()
			};

			const translation2: TranslationRecord = {
				translation_id: 'trans-2',
				document_url: 'https://multi.com',
				block_id: 'block-2',
				source_text: 'World',
				translated_text: 'Mundo',
				source_language: 'en',
				target_language: 'es',
				provider: 'openai',
				model: 'gpt-4',
				created_at: Date.now()
			};

			await manager.addTranslation(translation1);
			await manager.addTranslation(translation2);

			const translations = await manager.getTranslations('https://multi.com');
			expect(translations).toHaveLength(2);
		});
	});

	describe('Database Connection', () => {
		it('should close database connection', () => {
			manager.close();
			// Verify by checking internal state would require accessing private members
			// This test ensures close() doesn't throw
			expect(true).toBe(true);
		});
	});
});
