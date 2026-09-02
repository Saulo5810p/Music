/*
 * Copyright (C) 2007 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.android.music;

import android.database.AbstractCursor;

import java.util.ArrayList;

/**
 * Compat replacement for the internal, non-public
 * com.android.internal.database.ArrayListCursor. Exposes a list of
 * same-shaped ArrayLists (one per row, values in column order) as a Cursor,
 * the same way the original AOSP class did.
 */
public class ArrayListCursorCompat extends AbstractCursor {

    private final String[] mColumnNames;
    private final ArrayList<ArrayList> mRows;

    public ArrayListCursorCompat(String[] columnNames, ArrayList<ArrayList> rows) {
        mColumnNames = columnNames;
        mRows = rows;
    }

    private Object valueAt(int column) {
        return mRows.get(getPosition()).get(column);
    }

    @Override
    public int getCount() {
        return mRows.size();
    }

    @Override
    public String[] getColumnNames() {
        return mColumnNames;
    }

    @Override
    public String getString(int column) {
        Object v = valueAt(column);
        return v == null ? null : v.toString();
    }

    @Override
    public short getShort(int column) {
        return ((Number) valueAt(column)).shortValue();
    }

    @Override
    public int getInt(int column) {
        return ((Number) valueAt(column)).intValue();
    }

    @Override
    public long getLong(int column) {
        return ((Number) valueAt(column)).longValue();
    }

    @Override
    public float getFloat(int column) {
        return ((Number) valueAt(column)).floatValue();
    }

    @Override
    public double getDouble(int column) {
        return ((Number) valueAt(column)).doubleValue();
    }

    @Override
    public boolean isNull(int column) {
        return valueAt(column) == null;
    }
}
