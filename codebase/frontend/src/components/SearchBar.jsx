import { Search, X } from 'lucide-react';
import { useState, useEffect, useCallback } from 'react';

export function SearchBar({ onSearch, placeholder = 'Search...', debounceMs = 300 }) {
  const [query, setQuery] = useState('');

  const debouncedSearch = useCallback(
    debounce((value) => {
      onSearch(value);
    }, debounceMs),
    [onSearch, debounceMs]
  );

  useEffect(() => {
    debouncedSearch(query);
    return () => debouncedSearch.cancel();
  }, [query, debouncedSearch]);

  const handleChange = (e) => {
    setQuery(e.target.value);
  };

  const handleClear = () => {
    setQuery('');
    onSearch('');
  };

  return (
    <div className="relative max-w-md">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
      <input
        type="text"
        value={query}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
      />
      {query && (
        <button
          onClick={handleClear}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          aria-label="Clear search"
        >
          <X className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}

function debounce(fn, delay) {
  let timeoutId;
  const debouncedFn = (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
  debouncedFn.cancel = () => clearTimeout(timeoutId);
  return debouncedFn;
}