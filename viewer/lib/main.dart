import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter/services.dart' show rootBundle;

void main() {
  runApp(const RecipeApp());
}

class Recipe {
  final String title;
  final String chapter;
  final int serves;
  final int duration;
  final List<String> ingredients;
  final List<String> steps;
  final List<String> images;
  final String notes;

  Recipe({
    required this.title,
    required this.chapter,
    required this.serves,
    required this.duration,
    required this.ingredients,
    required this.steps,
    this.images = const [],
    this.notes = '',
  });

  factory Recipe.fromJson(Map<String, dynamic> json) => Recipe(
    title: json['Name'],
    chapter: json['Kapitel'],
    serves: json['Serves'],
    duration: json['Dauer'],
    ingredients: List<String>.from(json['Zutaten']),
    steps: List<String>.from(json['Anleitung']),
    images: json['Bild'] == null ? [] : List<String>.from(json['Bild']),
    notes: json['Notes'] ?? '',
  );
}

class RecipeApp extends StatelessWidget {
  const RecipeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
        Locale('de'),
      ],
      home: RecipeHomePage(),
    );
  }
}

class RecipeHomePage extends StatefulWidget {
  @override
  State<RecipeHomePage> createState() => _RecipeHomePageState();
}

class _RecipeHomePageState extends State<RecipeHomePage> {
  List<Recipe> allRecipes = [];
  String query = '';

  @override
  void initState() {
    super.initState();
    loadRecipes();
  }

  Future<void> loadRecipes() async {
    final jsonString = await rootBundle.loadString('assets/recipes.json');
    final data = json.decode(jsonString);
    final docs = data['documents'] as List;
    setState(() {
      allRecipes = docs.map((e) => Recipe.fromJson(e)).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    List<Recipe> filtered = allRecipes
        .where((r) => r.title.toLowerCase().contains(query.toLowerCase()))
        .toList();

    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.appTitle),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: TextField(
              decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: AppLocalizations.of(context)!.searchHint
              ),
              onChanged: (value) {
                setState(() => query = value);
              },
            ),
          ),

          Expanded(
            child: ListView.builder(
              itemCount: filtered.length,
              itemBuilder: (context, index) {
                final recipe = filtered[index];
                return ListTile(
                  title: Text(recipe.title),
                  subtitle: Text('${recipe.chapter} · ${recipe.duration} min'),
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => RecipeDetailPage(recipe: recipe),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class RecipeDetailPage extends StatelessWidget {
  final Recipe recipe;

  const RecipeDetailPage({super.key, required this.recipe});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: Text(recipe.title),
          bottom: TabBar(tabs: [
            Tab(text: AppLocalizations.of(context)!.ingredientsTab),
            Tab(text: AppLocalizations.of(context)!.stepsTab),
          ]),
        ),
        body: TabBarView(
          children: [
            ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text('${AppLocalizations.of(context)!.serves}: ${recipe.serves}'),
                Text('${AppLocalizations.of(context)!.duration}: ${recipe.duration} ${AppLocalizations.of(context)!.minutes}'),
                const SizedBox(height: 12),
                ...recipe.ingredients
                    .map((i) => Padding(
                  padding: const EdgeInsets.only(bottom: 8.0),
                  child: Text('- $i'),
                ))
                    .toList(),
              ],
            ),

            ListView(
              padding: const EdgeInsets.all(16),
              children: recipe.steps
                  .map((s) => Padding(
                padding: const EdgeInsets.only(bottom: 12.0),
                child: Text('• $s'),
              ))
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }
}
